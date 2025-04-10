package io.confluent.devrel.v2.kafka

import io.confluent.devrel.Membership
import io.confluent.devrel.datacontracts.shared.BaseConsumer
import io.confluent.kafka.serializers.AbstractKafkaSchemaSerDeConfig
import org.apache.kafka.clients.consumer.ConsumerConfig

class MembershipConsumer: BaseConsumer<String, Membership>(mapOf(
    ConsumerConfig.GROUP_ID_CONFIG to "app-schema-v2",
    ConsumerConfig.AUTO_OFFSET_RESET_CONFIG to "earliest",
    ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG to "org.apache.kafka.common.serialization.StringDeserializer",
    ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG to "io.confluent.kafka.serializers.KafkaAvroDeserializer",
    AbstractKafkaSchemaSerDeConfig.LATEST_COMPATIBILITY_STRICT to true,
    AbstractKafkaSchemaSerDeConfig.USE_LATEST_WITH_METADATA to "major_version=2"
)
) {
    override fun consumeRecord(key: String, value: Membership) {
        logger.info("v2 - Received Membership ${key}, ${value}")
    }
}