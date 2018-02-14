# Porter

> Porter is perillaroc-data-converter

A simple GrADS binary data tool for processing and trancoding.

It is currently supported to convert GrADS binary data to [MICAPS](http://www.micaps.cn) type 4 data.

## Installation

Download the latest code from Github and install using:

```bash
python setup.py install
```

## Getting started

Follow the steps below to convert GrADS binary data to MICAPS.4 data:

1. Create a config file.

    See example config files in directory `test/grads2micaps`.

2. Run the `porter` command.

    ```
    porter grads-convert config-file-path-list
    ```

    `config-file-path-list` is config file list。

## Config file

A simple config file for grads-convert:

```json
{
    "ctl": "path-to-ctl-file",
    "output_dir": "output-dir",
    "start_time": "YYYYMMDDHH",
    "forecast_time": "HHH",
    "records": [
        {
            "name": "variable name",
            "level": 1000,
            "level_type": "level_type(default multi)",
            "target_type": "type to be converted to (such as micaps.4)",
            "value": "value expr in which x is the original value(such sa 'x - 273.16')"
        }
    ]
}
```

## Acknowledgements

`porter` refers to some transcoding projects created by two predecessors. 
Due to privacy issues, I can not write their contact information. 
Thanks to their wonderful programs, and I benefit from their codes greatly.

## License

Copyright &copy; 2014-2018 Perilla Roc.

`porter` is licensed under [The MIT License](https://opensource.org/licenses/MIT).
