import findspark
findspark.init()
from pyspark.sql.functions import col, regexp_replace
from pyspark import SparkConf
from pyspark.sql import SparkSession
from pyspark.conf import SparkConf
SparkSession.builder.config(conf=SparkConf())
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, ArrayType,BinaryType
from pyspark.sql.functions import from_json,explode
from cassandra.cluster import Cluster

spark = SparkSession.builder \
    .appName("KafkaSparkIntegration") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.4,"
            "com.datastax.spark:spark-cassandra-connector_2.12:3.2.0,"
            "org.mongodb.spark:mongo-spark-connector_2.12:3.0.1") \
    .config('spark.cassandra.connection.host', 'localhost') \
    .getOrCreate()


df = spark.readStream \
  .format("kafka") \
  .option("kafka.bootstrap.servers", "localhost:9092") \
  .option("subscribe", "jane__essadi__topic") \
  .option("startingOffsets", "earliest") \
  .load()

value_df = df.selectExpr("CAST(value AS STRING)")



data_schema = StructType([
    StructField("results", ArrayType(
        StructType([
            StructField("gender", StringType(), True),
            StructField("name", StructType([
                StructField("title", StringType(), True),
                StructField("first", StringType(), True),
                StructField("last", StringType(), True)
            ]), True),
            StructField("location", StructType([
                StructField("street", StructType([
                    StructField("number", IntegerType(), True),
                    StructField("name", StringType(), True)
                ]), True),
                StructField("city", StringType(), True),
                StructField("state", StringType(), True),
                StructField("country", StringType(), True),
                StructField("postcode", IntegerType(), True),
                StructField("coordinates", StructType([
                    StructField("latitude", StringType(), True),
                    StructField("longitude", StringType(), True)
                ]), True),
            ]), True),
            StructField("email", StringType(), True),
            StructField("login", StructType([
                StructField("uuid", StringType(), True),
                StructField("username", StringType(), True),
                StructField("password", StringType(), True)
            ]), True),
            StructField("dob", StructType([
                StructField("date", StringType(), True),
                StructField("age", IntegerType(), True)
            ]), True),
            StructField("registered", StructType([
                StructField("date", StringType(), True),
                StructField("age", IntegerType(), True)
            ]), True),
            StructField("phone", StringType(), True),
            StructField("cell", StringType(), True),
            StructField("nat", StringType(), True)
        ]), True),
    True)
])


selected_df = value_df.withColumn("values", from_json(value_df["value"], data_schema)).selectExpr("explode(values.results) as results_exploded")

result_df = selected_df.select(
    F.col("results_exploded.login.uuid").alias("id"),
    F.col("results_exploded.gender").alias("gender"),
    F.col("results_exploded.name.title").alias("title"),
    F.concat_ws(" ",
            F.col("results_exploded.name.last"),
            F.col("results_exploded.name.first")).alias("fullname"),
    F.col("results_exploded.login.username").alias("username"),
    F.col("results_exploded.email").alias("email"),
    F.split(F.col("results_exploded.email"), "@").getItem(1).alias("domain_name"),
    F.col("results_exploded.phone").alias("phone"),
    F.concat_ws(", ",
            F.col("results_exploded.location.city"),
            F.col("results_exploded.location.state"),
            F.col("results_exploded.location.country")).alias("address"),
    F.round(F.datediff(F.current_date(), F.to_date(F.col("results_exploded.dob.date")))/365).alias("age"),
    F.col("results_exploded.registered.date").alias("inscription"),
    F.col("results_exploded.nat").alias("nationality")
)
#  encrypt  email,passowrd,phone,cell using SHA-256
result_df = result_df.withColumn("email", F.sha2(result_df["email"], 256))
result_df = result_df.withColumn("phone", F.sha2(result_df["phone"], 256))
result_df = result_df.withColumn("address", F.sha2(result_df["address"], 256))



print("-------------------- Connect to Cassandra -----------------------")

cassandra_host = 'localhost'
cassandra_port = 9042
keyspaceName = 'jane_keyspace'
tableName = 'users_table'


def connect_to_cassandra(host,port):
    try:
        cluster = Cluster([host],port=port)
        session = cluster.connect()
        print("Connection established successfully.")
        return session
    except:
        print("Connection failed.")

def create_cassandra_keyspace(session,keyspaceName):
    try:
        create_keyspace_query = """ CREATE KEYSPACE IF NOT EXISTS """+keyspaceName+ \
        """ WITH REPLICATION = {'class': 'SimpleStrategy', 'replication_factor': 1}"""
        session.execute(create_keyspace_query)
        print("Keyspace was created successfully.")
    except:
        print(f"Error in creating keyspace {keyspaceName}.")

def create_cassandra_table(session,tableName):
    try:
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {tableName} (
            id UUID PRIMARY KEY,
            gender TEXT,
            title TEXT,
            fullname TEXT,
            username TEXT,
            domain_name TEXT,
            email TEXT,
            phone TEXT,
            address TEXT,
            age INT,
            inscription TEXT,
            nationality TEXT,
        )
        """
        session.execute(create_table_query)
        print("table was created successfully.")
    except:
        print(f"Error in creating table {tableName}.")


session = connect_to_cassandra(cassandra_host,cassandra_port)
create_cassandra_keyspace(session,keyspaceName)
session.set_keyspace(keyspaceName)
create_cassandra_table(session,tableName)

result_df_clean = result_df.filter("id IS NOT NULL and age >= 18")

result_df_clean.writeStream \
    .outputMode("append") \
    .format("org.apache.spark.sql.cassandra") \
    .option("checkpointLocation", "./checkpoint/data") \
    .option("keyspace", keyspaceName) \
    .option("table", tableName) \
    .start()

# -----------------mongodb-----------


mongo_uri = "mongodb://localhost:27017"  # Replace with your MongoDB connection URI
mongo_db_name = "users_profiles"
collection_name = "user_collection"

# Save the data to MongoDB

def save_to_mongodb_collection(mongo_uri, mongo_db_name, collection_name, result_df_clean):
    result_df_mongo = result_df_clean.select(
        F.col("gender").alias("gender"),
        F.col("fullname").alias("fullname"),
        F.col("username").alias("username"),
        F.col("age").alias("age").cast(IntegerType()),
        F.col("inscription").alias("inscription"),
        F.col("nationality").alias("nationality"),
        F.col("domain_name").alias("domain_name"),
    )

    query = result_df_mongo.writeStream \
        .foreachBatch(lambda batchDF, batchId: batchDF.write \
            .format("mongo") \
            .option("uri", mongo_uri) \
            .option("database", mongo_db_name) \
            .option("collection", collection_name) \
            .mode("append") \
            .save()
        ) \
        .outputMode("append") \
        .start()
    query = result_df.writeStream.outputMode("append").format("console").start()
    query.awaitTermination()

save_to_mongodb_collection(mongo_uri, mongo_db_name, collection_name, result_df_clean)