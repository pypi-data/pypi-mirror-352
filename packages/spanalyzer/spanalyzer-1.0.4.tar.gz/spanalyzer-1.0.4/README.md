<h1 align='center'><strong>Spanalyzer</strong></h1>

<p align='center'>
    Get a comprehensive report on the telemetry implementation within your Python codebase.
</p>

<div align="center">

  ![Coverage](https://img.shields.io/badge/coverage-91%25-brightgreen)
  ![Tests](https://img.shields.io/badge/tests-62%20passed%2C%200%20failed-brightgreen)
  ![Python Version](https://img.shields.io/badge/python-3.10.16-blue?logo=python&logoColor=white)

</div>

---

### **1. Introduction**

**Spanalyzer** is a Python package that helps you analyze and audit the telemetry instrumentation (e.g., spans, metrics, events) within your codebase.

Once analyzed, the package generates a report summarizing or detailing telemetry coverage across your codebase.

---

### **2. Installation**

Install the package like any other Python library:

```bash
pip install spanalyzer
```

---

### **3. Usage**

The course of action of this package encompasses two procedures:
1. provide the path to the codebase you want to analyze;
2. pick the type of report you want to generate (**_basic_** or **_detailed_**);
3. provide the language of the codebase (**_python_** and **_java_** are currently supported).

#### **3.1. Basic Report**

The basic report will provide the user a very generic but clear view over the telemetry implementation within the codebase.

The output printed on the terminal will be as follows:

```bash
Script                    Spans    Traces    Metrics    Events    Attributes
----------------------------------------------------------------------------
script_1.py               ✓        ✓         ✓          ✓         ✓         
script_2.py               ✓        ✗         ✗          ✓         ✓         
script_3.py               ✓        ✓         ✓          ✗         ✓         
----------------------------------------------------------------------------
```

This kind of report can be useful during the development stage to get a glimpse of the type of telemetry resources we're allocating to the code being produced.

And you can obtain this report on the terminal by running the following command:
```bash
spanalyzer basic --path /path/to/codebase
```

#### **3.2. Detailed Report**

On the other hand, the detailed report, will not only capture what type of telemetry resources are being allocated to the codebase as you can also get further details about those resources.

In this report, we will have the list of scripts that were submitted to the analysis and per script details like the name of the span under usage, which metrics were captured, which events were recorded, etc. will all be part of this type of report.

Here's an example of the content of the detailed report:
```json
    "dsi_schema_assurance/validator.py": {
        "tracers": [
            {
                "func": "__name__",
                "line_number": 35,
                "args": null,
                "keywords": null
            }
        ],
        "functions": {
            "_is_inference_type_valid": {
                "docstring": "Check if the inference type is valid."
            },
            "_validate_key_inputs": {
                "docstring": "Validate we have the graphs we need."
            },
            "_get_datatypes": {
                "docstring": "Handler that will return the list of datatypes depending on the inference type\n        chosen.\n\n        Returns:\n            Dict[str, str]: A dictionary containing the datatypes for the injection.",
                "spans": [
                    {
                        "func": "_get_datatypes",
                        "line_number": 216,
                        "args": null,
                        "keywords": null
                    },
                    {
                        "func": "shacl",
                        "line_number": 232,
                        "args": null,
                        "keywords": null
                    },
                    {
                        "func": "both",
                        "line_number": 237,
                        "args": null,
                        "keywords": null
                    },
                    {
                        "func": "datatype_mismatch",
                        "line_number": 268,
                        "args": null,
                        "keywords": null
                    }
                ],
                "attributes": [
                    {
                        "func": "set_attribute",
                        "line_number": 217,
                        "args": {
                            "func": "span.set_attribute",
                            "args": [
                                "inference_type",
                                "self.inference_type"
                            ]
                        },
                        "keywords": null
                    },
                    {
                        "func": "set_attribute",
                        "line_number": 233,
                        "args": {
                            "func": "sub_span.set_attribute",
                            "args": [
                                "datatype_count",
                                "shacl_dtypes.shape"
                            ]
                        },
                        "keywords": null
                    },
                    {
                        "func": "set_attribute",
                        "line_number": 283,
                        "args": {
                            "func": "sub_span.set_attribute",
                            "args": [
                                "datatype_count",
                                {
                                    "func": "len",
                                    "args": [
                                        "combo_dtypes"
                                    ]
                                }
                            ]
                        },
                        "keywords": null
                    }
                ],
                "events": [
                    {
                        "func": "add_event",
                        "line_number": 269,
                        "args": {
                            "func": "sub_span.add_event",
                            "args": [
                                "Datatype Mismatch",
                                {
                                    "missing_records": "missing_records",
                                    "diff_records": "diff_records"
                                }
                            ]
                        },
                        "keywords": null
                    }
                ]
            },
            "_store_injected_data": {
                "docstring": "Stores the data graph with the datatypes injected.\n\n        Returns:\n            [str, str]: A string containing the directory and the path to the injected data."
            },
            "failure_report": {
                "docstring": "Build an error report from the data obtained by the validation from pyshacl library.\n\n        _Error Report Shape_:\n        {\n            'error_rate': 123,\n            'errors': [\n                'error_1',\n                'error_2',\n                'error_3',\n            ],\n            'raw_data': 'data_graph_as_xml'\n        }\n\n        Args:\n            raw_data (str): raw version of the data submitted for validation process\n            results_graph (Graph): The graph containing the validation results\n\n        Returns:\n            Dict[str, str]: A dictionary containing the error report",
                "spans": [
                    {
                        "func": "failure_report",
                        "line_number": 351,
                        "args": null,
                        "keywords": null
                    }
                ],
                "attributes": [
                    {
                        "func": "set_attribute",
                        "line_number": 352,
                        "args": {
                            "func": "span.set_attribute",
                            "args": [
                                "error_rate",
                                "number_of_violations"
                            ]
                        },
                        "keywords": null
                    },
                    {
                        "func": "set_attribute",
                        "line_number": 353,
                        "args": {
                            "func": "span.set_attribute",
                            "args": [
                                "errors",
                                "errors_lst"
                            ]
                        },
                        "keywords": null
                    }
                ]
            },
        }
    }
```

And you can obtain this report by running the following command:

```bash
spanalyzer detailed --path /path/to/codebase --output /path/to/output/file --language java
```

The output file will be a file containing the same information pointed out above.


---

### **A. Acknowledgements**

There's some considerations that are important to be taken into account:
- Due to the expidated nature of the development this package, and more specifically the java parser, leverages **`javalang`, which is only compatible with java versions up until version 8.**

---

### **B. Changelog**

- [ ] Add support for other telemetry resources;
- [x] Add support for other programming languages;
- [ ] Add telemetry to the package itself.