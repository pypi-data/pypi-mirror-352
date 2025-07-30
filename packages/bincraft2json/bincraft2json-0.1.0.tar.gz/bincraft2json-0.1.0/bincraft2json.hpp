/*
 * bincraft2json.hpp
 *
 * Copyright (c) 2025 @aymene69
 *
 * This header provides a function to decode a binary BinCraft file (optionally ZSTD-compressed)
 * and convert its aircraft data to a JSON array using nlohmann::json.
 *
 * Usage:
 *   #include "bincraft2json.hpp"
 *   nlohmann::json result = decodeBinCraftToJson("flight_data.bin", zstd_compressed=true);
 *
 * Requirements:
 *   - nlohmann::json (single-header, recommended: use the provided local json.hpp)
 *   - ZSTD (libzstd)
 *
 * IMPORTANT: To avoid ABI or version conflicts, always use #include "json.hpp" (local) instead of <nlohmann/json.hpp>.
 * Make sure to compile with -I. to prioritize the local header.
 *
 * This header is header-only and reusable in other C++ projects.
 *
 * All fields and decoding logic are self-contained. See README.md for details.
 */
#ifndef AIRCRAFT_TO_JSON_HPP
#define AIRCRAFT_TO_JSON_HPP

#include <string>
#include <vector>
#include <fstream>
#include <sstream>
#include <cstdint>
#include <cmath>
#include "json.hpp" // Always use the local header for compatibility
#include <zstd.h>
#include <iomanip>
#include <stdexcept>

/**
 * Aircraft struct: Holds all decoded fields for a single aircraft record.
 * All fields are public and mapped directly from the BinCraft binary format.
 */
struct Aircraft {
    std::string hex;
    double seen_pos;
    double seen;
    double lat;
    double lon;
    int32_t alt_baro;
    int32_t alt_geom;
    int16_t baro_rate;
    int16_t geom_rate;
    uint16_t nav_altitude_mcp;
    uint16_t nav_altitude_fms;
    double nav_qnh;
    double nav_heading;
    std::string squawk;
    double gs;
    double mach;
    double roll;
    double track;
    double track_rate;
    double mag_heading;
    double true_heading;
    int16_t wd;
    int16_t ws;
    int16_t oat;
    int16_t tat;
    uint16_t tas;
    uint16_t ias;
    uint16_t rc;
    uint16_t messages;
    std::string category;
    uint8_t nic;
    uint8_t emergency;
    std::string type;
    uint8_t airground;
    uint8_t nav_altitude_src;
    uint8_t sil_type;
    uint8_t adsb_version;
    uint8_t adsr_version;
    uint8_t tisb_version;
    uint8_t nac_p;
    uint8_t nac_v;
    uint8_t sil;
    uint8_t gva;
    uint8_t sda;
    uint8_t nic_a;
    uint8_t nic_c;
    double rssi;
    uint8_t dbFlags;
    std::string flight;
    std::string t;
    std::string r;
    uint8_t receiverCount;
    uint8_t nic_baro;
    uint8_t alert;
    uint8_t spi;
    std::vector<std::string> nav_modes;
};

/**
 * Helper functions for little-endian binary parsing.
 */
inline uint32_t read_uint32_le(const std::vector<uint8_t>& buffer, size_t offset) {
    return static_cast<uint32_t>(buffer[offset]) |
           (static_cast<uint32_t>(buffer[offset + 1]) << 8) |
           (static_cast<uint32_t>(buffer[offset + 2]) << 16) |
           (static_cast<uint32_t>(buffer[offset + 3]) << 24);
}
inline int32_t read_int32_le(const std::vector<uint8_t>& buffer, size_t offset) {
    return static_cast<int32_t>(read_uint32_le(buffer, offset));
}
inline uint16_t read_uint16_le(const std::vector<uint8_t>& buffer, size_t offset) {
    return static_cast<uint16_t>(buffer[offset]) |
           (static_cast<uint16_t>(buffer[offset + 1]) << 8);
}
inline int16_t read_int16_le(const std::vector<uint8_t>& buffer, size_t offset) {
    return static_cast<int16_t>(read_uint16_le(buffer, offset));
}
inline uint8_t read_uint8(const std::vector<uint8_t>& buffer, size_t offset) {
    return buffer[offset];
}

/**
 * genStr: Extracts a printable ASCII string from a byte range.
 */
inline std::string genStr(const std::vector<uint8_t>& data, size_t start, size_t end) {
    std::string s = "";
    for (size_t i = start; i < end && i < data.size(); ++i) {
        if (data[i] > 32 && data[i] < 127) {
            s += static_cast<char>(data[i]);
        } else if (data[i] == 0) {
            break;
        }
    }
    s.erase(s.find_last_not_of(" \t\n\r\f\v") + 1);
    return s;
}

/**
 * getType: Decodes the aircraft type field from a byte value.
 */
inline std::string getType(uint8_t t) {
    switch (t) {
        case 0: return "adsb_icao";
        case 1: return "adsb_icao_nt";
        case 2: return "adsr_icao";
        case 3: return "tisb_icao";
        case 4: return "adsc";
        case 5: return "mlat";
        case 6: return "other";
        case 7: return "mode_s";
        case 8: return "adsb_other";
        case 9: return "adsr_other";
        case 10: return "tisb_trackfile";
        case 11: return "tisb_other";
        case 12: return "mode_ac";
        default: return "unknown";
    }
}

/**
 * aircraftToJson: Converts an Aircraft struct to a nlohmann::json object.
 * Handles all fields, including nav_modes (vector<string>).
 */
inline nlohmann::json aircraftToJson(const Aircraft& ac) {
    nlohmann::json j;
    j["hex"] = ac.hex;
    j["seen_pos"] = ac.seen_pos;
    j["seen"] = ac.seen;
    j["lat"] = ac.lat;
    j["lon"] = ac.lon;
    j["alt_baro"] = (ac.airground == 1 ? "ground" : std::to_string(ac.alt_baro));
    j["alt_geom"] = ac.alt_geom;
    j["baro_rate"] = ac.baro_rate;
    j["geom_rate"] = ac.geom_rate;
    j["nav_altitude_mcp"] = ac.nav_altitude_mcp;
    j["nav_altitude_fms"] = ac.nav_altitude_fms;
    j["nav_qnh"] = ac.nav_qnh;
    j["nav_heading"] = ac.nav_heading;
    j["squawk"] = ac.squawk;
    j["gs"] = ac.gs;
    j["mach"] = ac.mach;
    j["roll"] = ac.roll;
    j["track"] = ac.track;
    j["track_rate"] = ac.track_rate;
    j["mag_heading"] = ac.mag_heading;
    j["true_heading"] = ac.true_heading;
    j["wd"] = ac.wd;
    j["ws"] = ac.ws;
    j["oat"] = ac.oat;
    j["tat"] = ac.tat;
    j["tas"] = ac.tas;
    j["ias"] = ac.ias;
    j["rc"] = ac.rc;
    j["messages"] = ac.messages;
    j["category"] = ac.category;
    j["nic"] = ac.nic;
    j["emergency"] = ac.emergency;
    j["type"] = ac.type;
    j["airground"] = ac.airground;
    j["nav_altitude_src"] = ac.nav_altitude_src;
    j["sil_type"] = ac.sil_type;
    j["adsb_version"] = ac.adsb_version;
    j["adsr_version"] = ac.adsr_version;
    j["tisb_version"] = ac.tisb_version;
    j["nac_p"] = ac.nac_p;
    j["nac_v"] = ac.nac_v;
    j["sil"] = ac.sil;
    j["gva"] = ac.gva;
    j["sda"] = ac.sda;
    j["nic_a"] = ac.nic_a;
    j["nic_c"] = ac.nic_c;
    j["rssi"] = ac.rssi;
    j["dbFlags"] = ac.dbFlags;
    j["flight"] = ac.flight;
    j["t"] = ac.t;
    j["r"] = ac.r;
    j["receiverCount"] = ac.receiverCount;
    j["nic_baro"] = ac.nic_baro;
    j["alert"] = ac.alert;
    j["spi"] = ac.spi;
    j["nav_modes"] = ac.nav_modes;
    return j;
}

/**
 * decodeBinCraftToJson: Decodes a BinCraft binary file (optionally ZSTD-compressed) and returns a JSON array of aircraft.
 * @param filename Path to the BinCraft file
 * @param zstd_compressed Set to true if the file is ZSTD-compressed
 * @throws std::runtime_error on file or decoding errors
 * @return nlohmann::json array of aircraft
 *
 * Example:
 *   nlohmann::json arr = decodeBinCraftToJson("flight_data.bin", true);
 */
inline nlohmann::json decodeBinCraftToJson(const std::string& filename, bool zstd_compressed = false) {
    std::ifstream file(filename, std::ios::binary);
    if (!file) throw std::runtime_error("Failed to open file: " + filename);
    std::vector<uint8_t> raw_data((std::istreambuf_iterator<char>(file)), std::istreambuf_iterator<char>());
    std::vector<uint8_t> data_buffer;
    if (zstd_compressed) {
        size_t decompressed_size_hint = ZSTD_getFrameContentSize(raw_data.data(), raw_data.size());
        if (decompressed_size_hint == ZSTD_CONTENTSIZE_ERROR) throw std::runtime_error("Corrupted or invalid ZSTD file.");
        if (decompressed_size_hint == ZSTD_CONTENTSIZE_UNKNOWN) decompressed_size_hint = raw_data.size() * 3;
        data_buffer.resize(decompressed_size_hint);
        size_t result = ZSTD_decompress(data_buffer.data(), data_buffer.size(), raw_data.data(), raw_data.size());
        if (ZSTD_isError(result)) throw std::runtime_error("ZSTD decompression error: " + std::string(ZSTD_getErrorName(result)));
        data_buffer.resize(result);
    } else {
        data_buffer = raw_data;
    }
    if (data_buffer.size() < 20) throw std::runtime_error("Insufficient binary data for header (less than 20 bytes).");
    uint32_t stride = read_uint32_le(data_buffer, 8);
    if (stride == 0 || data_buffer.size() < stride) return nlohmann::json::array();
    std::vector<Aircraft> aircraft_list;
    for (size_t off = stride; off + stride <= data_buffer.size(); off += stride) {
        Aircraft ac;
        ac.hex = [&]() {
            uint32_t raw_hex = read_int32_le(data_buffer, off) & ((1 << 24) - 1);
            std::stringstream ss;
            ss << std::hex << std::setw(6) << std::setfill('0') << raw_hex;
            return ss.str();
        }();
        ac.seen_pos = static_cast<double>(read_uint16_le(data_buffer, off + 4)) / 10.0;
        ac.seen = static_cast<double>(read_uint16_le(data_buffer, off + 6)) / 10.0;
        ac.lat = static_cast<double>(read_int32_le(data_buffer, off + 8)) / 1e6;
        ac.lon = static_cast<double>(read_int32_le(data_buffer, off + 12)) / 1e6;
        ac.alt_baro = static_cast<int32_t>(read_int16_le(data_buffer, off + 16)) * 25;
        ac.alt_geom = static_cast<int32_t>(read_int16_le(data_buffer, off + 18)) * 25;
        ac.baro_rate = read_int16_le(data_buffer, off + 20) * 8;
        ac.geom_rate = read_int16_le(data_buffer, off + 22) * 8;
        ac.nav_altitude_mcp = read_uint16_le(data_buffer, off + 24) * 4;
        ac.nav_altitude_fms = read_uint16_le(data_buffer, off + 26) * 4;
        ac.nav_qnh = static_cast<double>(read_int16_le(data_buffer, off + 28)) / 10.0;
        ac.nav_heading = static_cast<double>(read_int16_le(data_buffer, off + 30)) / 90.0;
        ac.squawk = [&]() {
            uint16_t raw_squawk = read_uint16_le(data_buffer, off + 32);
            std::stringstream ss;
            ss << std::setw(4) << std::setfill('0') << raw_squawk;
            return ss.str();
        }();
        ac.gs = static_cast<double>(read_int16_le(data_buffer, off + 34)) / 10.0;
        ac.mach = static_cast<double>(read_int16_le(data_buffer, off + 36)) / 1000.0;
        ac.roll = static_cast<double>(read_int16_le(data_buffer, off + 38)) / 100.0;
        ac.track = static_cast<double>(read_int16_le(data_buffer, off + 40)) / 90.0;
        ac.track_rate = static_cast<double>(read_int16_le(data_buffer, off + 42)) / 100.0;
        ac.mag_heading = static_cast<double>(read_int16_le(data_buffer, off + 44)) / 90.0;
        ac.true_heading = static_cast<double>(read_int16_le(data_buffer, off + 46)) / 90.0;
        ac.wd = read_int16_le(data_buffer, off + 48);
        ac.ws = read_int16_le(data_buffer, off + 50);
        ac.oat = read_int16_le(data_buffer, off + 52);
        ac.tat = read_int16_le(data_buffer, off + 54);
        ac.tas = read_uint16_le(data_buffer, off + 56);
        ac.ias = read_uint16_le(data_buffer, off + 58);
        ac.rc = read_uint16_le(data_buffer, off + 60);
        ac.messages = read_uint16_le(data_buffer, off + 62);
        uint8_t raw_category = read_uint8(data_buffer, off + 64);
        if (raw_category) {
            std::stringstream ss;
            ss << std::hex << std::uppercase << static_cast<int>(raw_category);
            ac.category = ss.str();
        } else {
            ac.category = "";
        }
        ac.nic = read_uint8(data_buffer, off + 65);
        uint8_t byte67 = read_uint8(data_buffer, off + 67);
        ac.emergency = byte67 & 0x0F;
        ac.type = getType((byte67 & 0xF0) >> 4);
        uint8_t byte68 = read_uint8(data_buffer, off + 68);
        ac.airground = byte68 & 0x0F;
        ac.nav_altitude_src = (byte68 & 0xF0) >> 4;
        uint8_t byte69 = read_uint8(data_buffer, off + 69);
        ac.sil_type = byte69 & 0x0F;
        ac.adsb_version = (byte69 & 0xF0) >> 4;
        uint8_t byte70 = read_uint8(data_buffer, off + 70);
        ac.adsr_version = byte70 & 0x0F;
        ac.tisb_version = (byte70 & 0xF0) >> 4;
        uint8_t byte71 = read_uint8(data_buffer, off + 71);
        ac.nac_p = byte71 & 0x0F;
        ac.nac_v = (byte71 & 0xF0) >> 4;
        uint8_t byte72 = read_uint8(data_buffer, off + 72);
        ac.sil = byte72 & 0x03;
        ac.gva = (byte72 & 0x0C) >> 2;
        ac.sda = (byte72 & 0x30) >> 4;
        ac.nic_a = (byte72 & 0x40) >> 6;
        ac.nic_c = (byte72 & 0x80) >> 7;
        uint8_t raw_rssi_byte = read_uint8(data_buffer, off + 86);
        ac.rssi = 10.0 * std::log10(static_cast<double>(raw_rssi_byte * raw_rssi_byte) / 65025.0 + 1.125e-5);
        ac.dbFlags = read_uint8(data_buffer, off + 87);
        ac.flight = genStr(data_buffer, off + 78, off + 87);
        ac.t = genStr(data_buffer, off + 88, off + 92);
        ac.r = genStr(data_buffer, off + 92, off + 104);
        ac.receiverCount = read_uint8(data_buffer, off + 104);
        uint8_t byte73 = read_uint8(data_buffer, off + 73);
        ac.nic_baro = (byte73 & 0x01);
        ac.alert = (byte73 & 0x02) >> 1;
        ac.spi = (byte73 & 0x04) >> 2;
        uint8_t nav_modes_byte = read_uint8(data_buffer, off + 66);
        if (nav_modes_byte & 0x01) ac.nav_modes.push_back("autopilot");
        if (nav_modes_byte & 0x02) ac.nav_modes.push_back("vnav");
        if (nav_modes_byte & 0x04) ac.nav_modes.push_back("alt_hold");
        if (nav_modes_byte & 0x08) ac.nav_modes.push_back("approach");
        if (nav_modes_byte & 0x10) ac.nav_modes.push_back("lnav");
        if (nav_modes_byte & 0x20) ac.nav_modes.push_back("tcas");
        aircraft_list.push_back(ac);
    }
    nlohmann::json j_array = nlohmann::json::array();
    for (const auto& ac : aircraft_list) {
        j_array.push_back(aircraftToJson(ac));
    }
    return j_array;
}

#endif
