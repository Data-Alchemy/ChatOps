# Start from the official OpenJDK 8 image
FROM openjdk:8-jdk-alpine

ARG SPARK_VERSION=3.1.2
ARG HADOOP_VERSION=3.2
ARG HIVE_VERSION=3.1.2

# Install bash, curl, Python, and pip
RUN apk add --no-cache bash curl python3 py3-pip

# Download and extract Spark
RUN mkdir -p /opt && cd /opt && \
    curl https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz | \
    tar -zx && \
    ln -s spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} spark

# Download and extract Hive
RUN mkdir -p /opt && cd /opt && \
    curl https://archive.apache.org/dist/hive/hive-${HIVE_VERSION}/apache-hive-${HIVE_VERSION}-bin.tar.gz | \
    tar -zx && \
    ln -s apache-hive-${HIVE_VERSION}-bin hive

# Set environment variables for Spark
ENV SPARK_HOME /opt/spark
ENV PATH $PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin:/usr/bin

# Set environment variables for Hive
ENV HIVE_HOME /opt/hive
ENV PATH $PATH:$HIVE_HOME/bin

# Set Python environment variables
ENV PYSPARK_PYTHON /usr/bin/python3
ENV PYSPARK_DRIVER_PYTHON /usr/bin/python3

# Set the working directory
WORKDIR $SPARK_HOME

# Install PySpark
COPY requirements.txt /$SPARK_HOME/conf/
RUN pip3 install -r /$SPARK_HOME/conf/requirements.txt
RUN mkdir -p /opt/spark/logs && \
    chmod -R 777 /opt/spark/logs

# Add Spark and Hive configuration files
COPY spark-defaults.conf $SPARK_HOME/conf/
COPY hive-site.xml $SPARK_HOME/conf/
COPY log4j.properties $SPARK_HOME/conf/



# Start the Spark master by default
CMD [ "bin/spark-class", "org.apache.spark.deploy.master.Master" ]
