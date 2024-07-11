# Making a Lambda Layer

Create a new virtual environment

```
python3 -m venv venv
source venv/bin/activate
```

Install the package in the virtual environment

```
pip install slack_sdk
```

Make a directory called `python` and move the `lib` directory in there

```
mkdir python
mv venv/lib python
```

Zip up python directory

*Go to Finder → Compress*

OR 

```
zip -r archive_name.zip directory_name
```

Create a new layer in the console

![image](https://github.com/ebanner/awakened-bot/assets/2068912/4cf968fe-0eb1-4f5f-8859-f9fb993babc1)
