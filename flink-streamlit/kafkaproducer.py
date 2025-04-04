from functools import partial
from confluent_kafka import Producer
from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.json_schema import JSONSerializer
from alpaca.data.live import StockDataStream
import streamlit as st

# set up alpaca websocket to receive stock events
wss_client = StockDataStream(st.secrets["ALPACA_KEY"], st.secrets["ALPACA_SECRET"])

# set up kafka client
print("Setting up Kafka client")

config_dict = {
    "bootstrap.servers": "",
    "sasl.mechanisms": "PLAIN",
    "security.protocol": "SASL_SSL",
    "session.timeout.ms": "45000",
    "sasl.username": st.secrets["SASL_USERNAME"],
    "sasl.password": st.secrets["SASL_PASSWORD"],
}


client_config = config_dict

# setting up the producer
producer = Producer(client_config)

srconfig = {
    "url": st.secrets["SR_URL"],
    "basic.auth.user.info": st.secrets["BASIC_AUTH_USER_INFO"],
}

# setting up the schema registry connection
schema_registry_client = SchemaRegistryClient(srconfig)

# schema for producer matching one in SPY topic in Confluent Cloud
schema_str = """{
  "$id": "http://example.com/myURI.schema.json",
  "$schema": "http://json-schema.org/draft-07/schema#",
  "additionalProperties": false,
  "description": "Sample schema to help you get started.",
  "properties": {
    "bid_timestamp": {
      "description": "The string type is used for strings of text.",
      "type": "string"
    },
    "price": {
      "description": "JSON number type.",
      "type": "number"
    },
    "symbol": {
      "description": "The string type is used for strings of text.",
      "type": "string"
    }
  },
  "title": "SampleRecord",
  "type": "object"
}"""


def serialize_custom_data(custom_data, ctx):
    return {
        "bid_timestamp": str(custom_data.timestamp),
        "price": int(custom_data.bid_price),
        "symbol": custom_data.symbol,
    }


# setting up the JSON serializer
json_serializer = JSONSerializer(
    schema_str, schema_registry_client, serialize_custom_data
)


def delivery_report(err, event):
    if err is not None:
        print(f'Delivery failed on reading for {event.key().decode("utf8")}: {err}')
    else:
        print(f"delivered new event from producer")


async def quote_data_handler(stockname, data):
    # this will run when `wss_client.subscribe_quotes(fn, stockname)` is called

    producer.produce(
        topic=stockname,
        key=stockname,
        value=json_serializer(
            data, SerializationContext(stockname, MessageField.VALUE)
        ),
        on_delivery=delivery_report,
    )
    producer.flush()


async def on_select(stockname):
    fn = partial(quote_data_handler, stockname)

    print(f"Subscribing to quote for {stockname}")

    wss_client.subscribe_quotes(fn, stockname)

    await wss_client._run_forever(),
