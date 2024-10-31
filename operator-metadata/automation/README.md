# Container build automation scripts

Automation scripts:
- Update bundle metadata with proper versioning and pull specs of new container builds
- Sync metadata between internal and external source repositories

## CPaaS execution workflow

These automation scripts are executed as part of the CPaaS container build pipeline
 
```
(1) CPaaS builds container images
(2) CPaaS executes these automation scripts, updating bundle metadata 
(3) CPaaS builds bundle image using updated bundle metadata 
```

## Tests

To run unit tests from `operator-metadata/automation/` directory run:

```
python3 -m venv venv
source venv/bin/activate
pip3 install pyaml
python -m unittest discover -t .. -v
```
