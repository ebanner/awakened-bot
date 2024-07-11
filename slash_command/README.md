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

Select compatible runtimes

![image](https://github.com/ebanner/awakened-bot/assets/2068912/7eb563d3-06bd-4b25-8785-84573eed7a7c)

Make SURE the compatible runtimes match the folder name in `lib` ‼️

<img width="798" alt="image" src="https://github.com/ebanner/awakened-bot/assets/2068912/80215924-22cf-4095-a8b2-5a63d46a8c97">

Create a new layer in the console

![image](https://github.com/ebanner/awakened-bot/assets/2068912/4cf968fe-0eb1-4f5f-8859-f9fb993babc1)

Add a lambda layer

![Screenshot 2024-07-11 at 3 53 57 PM](https://github.com/ebanner/awakened-bot/assets/2068912/e18bfd2e-519b-4c86-ab77-e0e7cc78fb3d)

Select lambda layer

![image](https://github.com/ebanner/awakened-bot/assets/2068912/3b3a4ce8-8faf-4b51-938c-92444611929a)
