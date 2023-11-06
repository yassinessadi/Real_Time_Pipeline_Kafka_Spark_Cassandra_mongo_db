# Project Context
>In a world where data is considered the new gold, it is imperative for organizations to be able to process and analyze data in real-time to make informed decisions. This program is designed for data professionals looking to acquire practical skills in implementing real-time data pipelines.

# Configuration and Dependencies :
Install the required libraries and dependencies for `Spark`, `pyspark` `Kafka`, `Cassandra`, and `MongoDB` `:`

## Kafka Installation & Configuration.
> To begin, we will first explain the installation process for Kafka and how to use it. Let's get started!
>To install Kafka, follow the [link](https://kafka.apache.org/downloads). In my case, I'm using Kafka version 3.6.0 [link to binary](href="https://downloads.apache.org/kafka/3.6.0/kafka_2.12-3.6.0.tgz).

After completing the installation, please make sure to extract the files and place them in the `C:/kafka` directory, naming it as desired. Next, open the Windows environment variables by typing `env` in the Windows search bar and add the following path: `C:\kafka\bin\windows`. Ensure that you select the `windows` directory inside the 'bin' folder.

Now, let's get the work done by running Kafka and Zookeeper.
#### Usage Instructions:
First, open the 'C:/kafka' directory with your command prompt and then type the following command To Start zookeeper & kafka:
```bash
zookeeper-server-start.bat ..\..\config\zookeeper.properties
```
open new command prompt and type:
```bash
kafka-server-start.bat ..\..\config\server.properties
```

To ensure everything is ready to go, please execute the following command below to create a topic. In my case, I named it 'first_topic,' but you can choose any name you prefer. Voilà, your topic is now created!
```bash
kafka-topics --bootstrap-server 127.0.0.1:9092 --topic first_topic --create --partitions 3 --replication-factor 1
```

Note: I'm using the IP address `127.0.0.1` (`localhost`) on the default port `9092`.

If you want to check or list your topics, please enter the following command:

```bash
kafka-topics.bat --list --bootstrap-server localhost:9092
```
Topic describe :
```bash
kafka-topics --bootstrap-server 127.0.0.1:9092 --topic user_profiles --describe
```
Create console producer :
```bash
kafka-console-producer.bat --broker-list localhost:9092 --topic first_topic
```
Create console consumer :
```bash
kafka-console-consumer.bat --bootstrap-server localhost:9092 --topic first_topic --from-beginning
```




## SPARK Installation & Configuration.
>later
## CASSANDRA Installation & Configuration.
>later
## MONGODB Installation & Configuration.

# Project:
## Kafka Producer using `(confluent-kafka)`:
> fetches random user data from the API (randomuser) and streams it to a Kafka topic, creating a data pipeline for further processing or analysis.

## PySpark Consumer using `(confluent-kafka)`:
```
-- Utilize the provided code to extract data from the Kafka topic "jane__essadi__topic."

-- Implement data transformations, which encompass parsing, validation, and data enrichment.
-- insert data into Cassandra

-- Execute data aggregation to derive insights, such as the count of users by nationality and the average user age. Store these results in MongoDB through the `save_to_mongodb_collection` function.

-- Configure debugging and monitoring mechanisms to track the pipeline's performance and identify potential issues.

-- Develop data visualization dashboards with Python Dash to present aggregated data effectively.

- Verify the accurate insertion of data into the Cassandra table and MongoDB collections.
```
## Data Visualization

- Employ Python Dash to construct data visualization dashboards, enabling the presentation of aggregated data, such as user counts by nationality and average user age.

# GDPR Compliance :
>In our professional context, our primary focus is on safeguarding our clients from data-related risks. We meticulously adhere to GDPR regulations, including refraining from collecting data on individuals below the age of `18`. Additionally, we prioritize securing `sensitive` client information through `encryption` or deletion, ultimately ensuring the safety of our users.