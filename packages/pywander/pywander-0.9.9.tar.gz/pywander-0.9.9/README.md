# pywander
a general purpose python module.


## USAGE
user just ust the package.
```
pip install pywander
```

## Console Scripts
### pywander_image
convert image
```
pywander_image convert --help
```
resize image

```text
pywander_image resize --help
```

### pywander_file
扫描该文件夹下的某种类型文件
```
pywander_file scan --help
```

执行该文件夹下的所有python脚本
```
pywander_file run --help
```

## TEST
local environment run 
```
pip install -e .
```
and run 

```
pytest
```
