#include <Arduino.h>

#include <stdint.h>
#include <string.h>

#include "component_config.hpp"

constexpr uint8_t START_BYTE = 0xAA;

constexpr uint16_t CRC16_INITIAL_VALUE = 0xFFFF;
constexpr uint16_t CRC16_POLYNOMIAL = 0x8408;

constexpr uint8_t PACKET_SIZE = 10;
constexpr uint8_t CRC_SIZE = 2;

uint16_t crc16(const uint8_t* data, uint8_t size) {
    uint16_t crc = CRC16_INITIAL_VALUE;

    for (uint8_t i = 0; i < size; ++i) {
        crc ^= data[i];

        for (uint8_t bit = 0; bit < 8; ++bit) {
            if ((crc & 1) != 0) {
                crc = (crc >> 1) ^ CRC16_POLYNOMIAL;
            } else {
                crc >>= 1;
            }
        }
    }

    return crc;
}

uint16_t read_uint16_le(const uint8_t* data) {
    return static_cast<uint16_t>(data[0]) |
           (static_cast<uint16_t>(data[1]) << 8);
}

float read_float(const uint8_t* data) {
    float value;

    memcpy(&value, data, sizeof(value));

    return value;
}

bool receive_packet(uint8_t* packet) {
    static uint8_t index = 0;

    while (Serial.available() > 0) {
        const uint8_t byte = Serial.read();

        if (index == 0) {
            if (byte != START_BYTE) {
                continue;
            }

            packet[index++] = byte;
            continue;
        }

        packet[index++] = byte;

        if (index == PACKET_SIZE) {
            index = 0;
            return true;
        }
    }

    return false;
}

bool verify_packet(const uint8_t* packet) {
    const uint16_t calculated_crc =
        crc16(packet, PACKET_SIZE - CRC_SIZE);

    const uint16_t received_crc =
        static_cast<uint16_t>(packet[8]) |
        (static_cast<uint16_t>(packet[9]) << 8);

    return calculated_crc == received_crc;
}

void execute_led_sequence(ComponentId component) {
    const uint8_t duration =
        static_cast<uint8_t>(component) + 1;

    Serial.print("LED duration: ");
    Serial.print(duration);
    Serial.println(" seconds");

    digitalWrite(LED_BUILTIN, HIGH);

    delay(static_cast<uint32_t>(duration) * 1000);

    digitalWrite(LED_BUILTIN, LOW);
}

void setup() {
    pinMode(LED_BUILTIN, OUTPUT);
    digitalWrite(LED_BUILTIN, LOW);

    Serial.begin(115200);
}

void loop() {
    uint8_t packet[PACKET_SIZE];

    if (!receive_packet(packet)) {
        return;
    }

    if (!verify_packet(packet)) {
        return;
    }

    const uint16_t packet_id = read_uint16_le(&packet[1]);

    const uint8_t raw_component_id = packet[3];

    if (!is_valid_component_id(raw_component_id)) {
        Serial.println("Invalid component ID");
        return;
    }

    const ComponentId component =
        static_cast<ComponentId>(raw_component_id);

    const float value = read_float(&packet[4]);

    Serial.print("Packet ID: ");
    Serial.println(packet_id);

    Serial.print("Component: ");
    Serial.println(component_name(component));

    Serial.print("Component ID: ");
    Serial.println(raw_component_id);

    Serial.print("Value: ");
    Serial.println(value);

    execute_led_sequence(component);
}
