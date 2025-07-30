/*
 * bincraft2json.cpp
 *
 * Author: @aymene69
 * License: MIT
 * Example usage for bincraft2json.hpp
 *
 * Compile with:
 *   g++ -std=c++17 -o bincraft2json bincraft2json.cpp -lzstd
 *
 * This program decodes a BinCraft binary file and prints the aircraft data as JSON.
 */
 
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "json.hpp"
#include "bincraft2json.hpp"

namespace py = pybind11;

// Fonction utilitaire pour convertir nlohmann::json en dict Python
py::dict json_to_dict(const nlohmann::json& j) {
    py::dict result;
    for (auto& [key, value] : j.items()) {
        if (value.is_object()) {
            result[key.c_str()] = json_to_dict(value);
        } else if (value.is_array()) {
            py::list list;
            for (const auto& item : value) {
                if (item.is_object()) {
                    list.append(json_to_dict(item));
                } else if (item.is_number()) {
                    list.append(item.get<double>());
                } else if (item.is_string()) {
                    list.append(item.get<std::string>());
                } else if (item.is_boolean()) {
                    list.append(item.get<bool>());
                } else if (item.is_null()) {
                    list.append(py::none());
                }
            }
            result[key.c_str()] = list;
        } else if (value.is_number()) {
            result[key.c_str()] = value.get<double>();
        } else if (value.is_string()) {
            result[key.c_str()] = value.get<std::string>();
        } else if (value.is_boolean()) {
            result[key.c_str()] = value.get<bool>();
        } else if (value.is_null()) {
            result[key.c_str()] = py::none();
        }
    }
    return result;
}

PYBIND11_MODULE(bincraft2json, m) {
    m.doc() = "BinCraft to JSON converter"; // optional module docstring

    m.def("decode_bincraft", [](const std::string& filename, bool zstd_compressed) {
        try {
            nlohmann::json result = decodeBinCraftToJson(filename, zstd_compressed);
            return json_to_dict(result);
        } catch (const std::exception& e) {
            PyErr_SetString(PyExc_RuntimeError, e.what());
            throw py::error_already_set();
        } catch (...) {
            PyErr_SetString(PyExc_RuntimeError, "Une erreur inconnue s'est produite");
            throw py::error_already_set();
        }
    }, "Decode a BinCraft binary file to JSON",
        py::arg("filename"),
        py::arg("zstd_compressed") = false
    );
}