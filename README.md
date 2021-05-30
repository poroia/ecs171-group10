# ecs171-group10

Due May 26

## Project Setup
0. Create pipenv and activate
  ```bash
    $ mkdir .venv/ # from project root
    $ pipenv shell
  ```
1. Install all dependencies 
  ```bash
    $ pipenv install
  ```
_Note:_
- _During the install, you might get an error setting up netifaces. Follow instructions here: https://stackoverflow.com/questions/64261546/python-cant-install-packages_
- _Also, if you run into errors with conflicting packages or individual packages, you can try doing steps 0 and 1 again (deleting the old the `env/` folder)_

2. Run the app
  ```bash
    $ streamlit run src/app.py
  ```

## Prototyping
Figma Link: https://www.figma.com/file/uErqjg73OIypOfXbNUqsfS/ecs171-group10

## Sprint 1: May 8 - May 13
Tasks:
- Project and environment setup: May 9
- Website prototyping: May 13
- Design of heatmap: May 13
- Plots of Symptoms Model

## Sprint 2: May 13 - 20
Tasks:
- Facial Model: May 20
- Symptoms Model: May 20
- Deaths Model: May 20

## Methods
- Facial Recognation: Convolutional Neural Network
- Symptoms Model: Linear Regression
- Deaths Mode: Logistics Regression

## Contribution

### Heming Ma

#### In-Progress
- Build the CNN Model for facial recognation

#### Done
- none

### Ray Ngan

#### In-Progress
- 

#### Done
- Finsihed building the Logistics Regession Model for patient's sysmptoms

### Vlad Plagov

#### In-Progress
- Working on the video for demo

#### Done
- Found a more fresh version of the data-set we currently have. To access:
    - Google Drive: https://drive.google.com/file/d/1byRlHTzPTuRy6JvKKt_lb-4uuANTQxSo/view?usp=sharing
    - VAERS website directly: https://vaers.hhs.gov/data/datasets.html?
    - VAERS data retrieval tool: https://wonder.cdc.gov/vaers.html
    - Documentation: https://wonder.cdc.gov/wonder/help/vaers.html#
- Finished on Logistic Regression Model for patient's outcomes

### Eric Bair

#### In-Progress
- Integrate facial recognition model into Streamlit (image capture/image upload)
- Testing webapp locally
- Working on demo video
- Working on final report

#### Done
- none

### Bryan Zhang

#### In-Progress
- Prototype webpage

#### Done
- Setup branch protections
- Setup development environment for web framework
- Setup deployment pipeline
- webcam

#### Jessy Huang

#### In-Progress
- Working on final report (solutions and conclusion)

#### Done
- final report (introduction - last half)
