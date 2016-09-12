# BORA - Build Once Run Always
BORA is a static monitoring framework, which aims to minimize the maintaining effort on the page and offers a flexible way to add and remove data items. Also, BORA addresses the limitation of ADEI server by building a retrofit interface that is capable of handling concurrent connections.

<br />
##Installation
Following demonstrates an example on BORA installation guide in openSUSE operating system. 

**Step 1**: <br />Start up a Terminal session and clone the bora.git list files into the desired path by copying the given web url into the following command line:

```sh
$ git clone https://github.com/kit-ipe/bora.git
```

**Step 2**: <br />After cloning, add the background image that you wish to design into static file under bora. 

**Step 3**: <br />In order to execute the pip-command, inside the terminal window, first change the directory path into bora.git and then feed in the following command line:

```sh
$ sudo easy_install pip
```

**Step 4**: <br />All the missing modules (pyyaml, requests and tornado) have been compiled inside the requirement.txt file. Install them using the following command line:

```sh
$ pip install -r requirements.txt
```

**Step 5**: <br />After the installations have finished, run the following python script and key in all the requested information:

```sh
$ python start.py
```

**Step 6**: <br />Finally, run the python script below: 

```sh
$ python core.py
```

**Step 7**: <br />When the program runs successfully, the following message will be shown:

```sh
Start torrenting...
Debugging...
```

**Step 8**: <br />Start up a web browser and go to the local designer page: http://localhost:\<port\>/designer and the status display page: http://localhost:\<port\>/status. For the access, you will be asked for the username and password, which you have previously defined during step 4. 

**Step 9**: <br />After entering the sites, you will be directed into a page with the previously added background image. Now, you are allowed to design the background image with the registered data.

<br />
##Usage

In principle, there are 2 viewer modes in BORA: designer mode and status mode. In designer mode  (http://localhost:\<port\>/designer), users are allowed to style the data with multifarious features whereas the status mode (http://localhost:\<port\>/status) displays the data styling from the designer mode to the viewers. 

**Data registration**

Before proceeding to data styling, all data need to be registered. Following shows an example of data registration for Katrin-Adei server:

The URL for data registration should exhibit the following format and attributes:

```sh
http://ipepc57.ipe.kit.edu:<port>/add/<server>/<db_name>/<db_group>/<sensor> 
```

A python script has been developed and stored under '/bora/res/adei2rest.py/' to generate the desired format of URL for purpose of data registration. 

Firstly, in the field of search browser inside katrin-adei server ('http://katrin.kit.edu/adei-katrin/'), enter the corresponding katrin number for a specified sensor. After searching and selecting the desired sensor, copy the web URL at the top the web browser. Switch back to the Terminal window, change the directory path into res file in bora and enter the following command line:

```sh
$ python adei2rest.py <sensor_name> 'copied web URL'
```
	
Then, copy the generated URL into the web browser and a message *”success”:”Data entry inserted.”* will appear.

**Data styling**

Inside the designer mode, you will notice there is an input field at the bottom of the web browser and you can choose to either hide or show it by clicking the button `Show/Hide` which is located at the bottom left of the web browser.

The input section *'Variable'* stores all the registered data. In order to style the data, first you need to select a data from this section. For the selected data, you need to define its type. Following explains all the available data types in BORA.

* **Data** <br />This data type is for defining a data with numerical value. After defining your data to this type, you can choose to either add a header and a unit to your data value, specify the font size, or even give a condition and equation to the data. For example, when you enter the number 200 inside the input section *'larger than (red)'*, it means that when the data value is greater than 200, its font will change to red color, or if you enter an equation with variable x as your data value like x+100 inside the input field *'Equation'*, this means that the data value will automatically increased by 100.       

* **Valve** <br />To insert an valve image, you can choose to use this data type. For defining this data type, you are required to set a value for it. For example, inside the input field *'unit'*, you need to specify dictionary case like *{“1”:“on” , “0”:”off”}* which means if the retrieved data value equals to 1, then an image of green colored valve will be added or red colored valve for input value 0, otherwise grey colored valve for none.
 
* **Integer-to-string** <br />When you wish to assign each data values to a specific definition, for example, input value 0 for Shutdown or input value 1 for Start-up, you can use this data type. This data type will analyze the retrieved data and print out the corresponded definition which you have previously defined. Likewise, for defining this data type, you need to specify a dictionary case inside the input field *'unit'* such as *{“0”:”Shutdown” , “1”:”Start-up”}*. Optionally, you can define each cases with a color code under the input field *'condition (red)'*. For example, *{“0”:”#f00” , “1”:”#008000”}*.

* **Header** <br />This data type allows you to insert a header without any pre-registered data. Thus, you need not to select any data from the input field *'Variable'* beforehand. Inside the input field *'title'*, you can just enter the header u wish and adjust the font size.

* **Calc** <br />With this function Calc, you are allowed to carry out any mathematical operations like adding, subtracting, multiplying or dividing the data values. Just like the data type Header, selecting a data from the input field *'Variable'* is not required. Next, you will need to write down the mathematical equations with the corresponded katrin number in squared brackets. An example for addition, [*katrin number 1*] + [*katrin number 2*].

Inside the drop-down input list of *'Attribute'*, there are two selections: *'Normal'* and *'Virtual'*. The selection *'Normal'* is for first time data inserting. If you wish to insert the same data for second time, you will need to change the selection *'Normal'* to *'Virtual'*, so that the same data will be virtually created again.


After finish defining all the required inputs, click the button `Add` at the bottom of the input fields. The respectively data will be inserted onto the background image and you can freely position it inside the image or you can also remove the inserted data by clicking the button `Remove`. Finally, hit the button `Save` to save the design which will later be displayed in the status mode.
