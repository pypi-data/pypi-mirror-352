
# 🚀 Installation Guide

DL_Track_US is designed with ease-of-use in mind. Whether you're a developer or completely new to coding, getting started is simple.

We provide **two ways** to install DL_Track_US:

---

## Option 1: Download the Installer (Recommended for Beginners & Windows only)

> **No programming required**

1. Visit our [OSF project page](https://osf.io/7mjsc/?view_only=) and anvigate to `Files/v0.3.0/´
2. Download and unzip the file: `DL_Track_US_example0.3.0.zip`
3. Inside the unzipped folder, open:  
   `DL_Track_US_example/DL_Track_US_Installer/DLTrackUS_Installer_Windows.exe`
4. Follow the instructions in the installation wizard.
5. Double-click the desktop icon to launch the **DL_Track_US GUI**

> If you want to change the analysis settings, **run DL_Track_US as administrator**.

You can now test the app using the provided example files.  
Check our [Tutorial](https://paulritsche.github.io/DL_Track_US/) and [Testing](https://paulritsche.github.io/DL_Track_US/) sections for more.

⚠️ **Note:** The DL_Track_US installer is available for Windows only. We are working on a MacOS version.

⚠️ You might see a warning from your antivirus software. You can safely dismiss it, this app is secure and verified.

---

## Option 2: Install via pip and GitHub (Recommended for Developers & MacOS)

> Ideal for customization, development, or contributing

---

### Step 1 - Install Anaconda

- Download and install [Anaconda](https://www.anaconda.com/download)
- Be sure to check the box:  
  *Add Anaconda to my PATH environment variable*

---

### Step 2 - Create a virtual environment

```bash
conda create -n DL_Track_US0.3.0 python=3.10
conda activate DL_Track_US0.3.0
```

---

### Step 3 - Install DL_Track_US

#### **Windows users:**

```bash
pip install DL-Track-US==0.3.0
```

#### **MacOS users:**

1. Download the repo or just the `requirements.txt` file from  
   [GitHub](https://github.com/PaulRitsche/DL_Track_US)
2. Navigate to the folder where `requirements.txt` is located:

```bash
cd path/to/DL_Track_US
```

3. Install dependencies and the package:

```bash
pip install -r requirements.txt
python -m pip install -e .
```

⚠️ **Note:** DL_Track_US was tested on Windows 10 and 11 as well as M1/M2 Macs.

---

### Step 4 - Start the DL_Track_US GUI

You have two options:

#### Option A *From the installed package*:

```bash
python -m DL_Track_US
```

#### Option B *From the cloned repository*:

```bash
cd DL_Track_US/DL_Track_US
python DL_Track_US_GUI.py
```

---

## Optional: GPU Setup for Faster Inference

> For **Windows/NVIDIA** users:

1. Install [NVIDIA GPU drivers](https://www.nvidia.com/Download/index.aspx?lang=en-us)
2. Download:
   - [CUDA 11.2](https://developer.nvidia.com/cuda-11.2.0-download-archive)
   - [cuDNN 8.5](https://developer.nvidia.com/rdp/cudnn-archive)
3. Follow this [video tutorial](https://www.youtube.com/watch?v=OEFKlRSd8Ic) (minutes 9-13)

> For **Mac (M1/M2)** users:

- Follow this [Apple Silicon TensorFlow guide](https://caffeinedev.medium.com/how-to-install-tensorflow-on-m1-mac-8e9b91d93706) for optional GPU support

---

## Need Help?

- Visit the [DL_Track_US Q&A on GitHub](https://github.com/PaulRitsche/DL_Track_US/discussions/categories/q-a)
- Tag your post with **Problem**
- Attach screenshots or logs if possible

We're happy to help you get up and running!
