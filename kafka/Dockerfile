FROM confluentinc/cp-kafka:7.5.0

# Configure Kafka for Render (single broker, no Zookeeper dependency via KRaft)
ENV KAFKA_NODE_ID=1 \
    KAFKA_PROCESS_ROLES=broker,controller \
    KAFKA_CONTROLLER_QUORUM_VOTERS=1@kafka:29093 \
    KAFKA_LISTENERS=PLAINTEXT://0.0.0.0:29092,CONTROLLER://0.0.0.0:29093 \
    KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:29092 \
    KAFKA_CONTROLLER_LISTENER_NAMES=CONTROLLER \
    KAFKA_INTER_BROKER_LISTENER_NAME=PLAINTEXT \
    KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1 \
    KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR=1 \
    KAFKA_TRANSACTION_STATE_LOG_MIN_ISR=1 \
    KAFKA_AUTO_CREATE_TOPICS_ENABLE=true \
    KAFKA_LOG_DIRS=/var/lib/kafka/data

# Health check
HEALTHCHECK --interval=10s --timeout=5s --start-period=30s --retries=5 \
    CMD kafka-broker-api-versions --bootstrap-server localhost:29092 || exit 1

EXPOSE 29092

CMD ["sh", "-c", "kafka-server-start /etc/kafka/kafka-server.properties"]
