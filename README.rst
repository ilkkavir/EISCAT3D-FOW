Overview
========

A simple python script that plots EISCAT3D sites on map with a simple beam configuration and the 3-static field-of-views at 100 km and 300 km altitudes. 

The script was developed with google gemini AI with some manual polishing afterwards. 

Prerequisites
=======

The script works in a mamba environment generated with the following command. Module version information may (or may not) follow later... ::

  mamba create -n e3d_figure -c conda-forge python=3.11 matplotlib cartopy numpy shapely -y
  mamba activate e3d_figure


Example
===========

Run the script with the command ::

  python E3DonMapShaded.py
   
