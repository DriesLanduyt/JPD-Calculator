# Joint probability distribution (JPD) calculator

Python scripts to derive (conditional) joint probability distributions for variable pairs of a BBN model

© 2016, Dries Landuyt (<mailto:drieslanduyt@gmail.com>)

###Dependencies

Copy the `Netica.dll` file which can be found in your local installation of Netica or at the [Norsys website](https://www.norsys.com) to the same directory as the scripts you can find here (`JPDCalculator.py` and `NeticaCode.py`)

Whether you need the 32bit or 64bit version of the `Netica.dll` will depend on your Python installation. To check this, run the following code in your Python console:

```
import struct
print 8*struct.calcsize("P")
```

Note that these scripts are written in Python 2.x and will not run in Python 3.x

###Usage

```
import JPDCalculator as jpdc
import NeticaCode as nc

#Open network
net = nc.OpenBayesNet('D:/irectory/of/network/file/netname.neta')
print net

#Calculate JPD
JPDdata = jpdc.JPD(net,['nodename1','nodename2'])
  #or
JPDdata_all = jpdc.allJPDs(net)

#Plot JPD
jpdc.drawJPD(JPDdata)
  #or
jpdc.drawAllJPDs(JPDdata_all)

#To calculate JPD conditional on the fact that node x is in state x
JPDdata = jpdc.cJPD(net,['nodename1','nodename2'],'nodenamex','statenamex')
```
