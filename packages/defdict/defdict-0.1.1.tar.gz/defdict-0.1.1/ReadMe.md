# DefDict

## Ver. 0.1.xx
The current version is imported from REMS which originally included all DefDict codes. 

## What is DefDict
DefDict is an extension of a dictionary, but with definitions + typing like in TypedDict or named struct.

Key differences are:
* Many options to set the values
* Many ways to output values
* Filter out based on a subset of keys
* Convert compatible definitions to its own definitions
* Object-oriented structure and native nested DefDict handling

## Create a new DefDict
```python
# x,y,z and they are float
# this will enforce all values are float. Simply float(value) will be called at this moment.
pos = DefDict(dict(x=float,y=float,z=float))

# rotation
rot = DefDict(dict(qx=float,qy=float,qz=float, qw=float))
# x,y,z and rotation
pos_rot = DefDict((dict(x=float,y=float,z=float),
                   dict(qx=float,qy=float,qz=float, qw=float))) # Tuple of two dicts
```

## Set values
```python
d = DefDict(dict(x=float,y=float,z=float))
# set value
d.update({'x': 1, 'y':2, 'z':3})
# or you can use equality, but not recommended to avoid typos (missing .data, i.e.) 
d.data = {'x': 1, 'y':2,'z':3}
# you can use tuple, list, ndarray, or just single value
d.update(('x',1))
d.update([1,2,3])          # positional assignment
d.update(np.array[1,2,3])  # positional assignment
d.update(1)                # positional assignment
# you can do like normal dict
d['x'] = 1
```

## Get values:
```python
d = DefDict(dict(x=float,y=float,z=float))  

d.update({'x': 1, 'y':2, 'z':3})
d.dict() -> {'x': 1, 'y':2, 'z':3}
d.data() -> {'x': 1, 'y':2, 'z':3}
d.list() -> [1,2,3]
d.ndarray()  -> ndarray([1,2,3])
d.ndtall()  -> ndarray([[1],[2],[3]]) #tall vector
d.ndarray((1,3))  -> # reshaped ndarray

# You can do like normal dict
d.get('x') -> 1
d['x'] -> 1

# For keys
d.list_keys()  -> ['x','y','z']

# you can get certain values only:
d.get('x')           -> {'x':1}
d.get(['x','y'])     -> {'x': 1, 'y':2}
d.get({'x':0,'y':0}) -> {'x': 1, 'y':2}  # ignore values in the original dictionary
```

You can filter and get: 
```python
d.filter(['x','y']).list()    -> [1,2]
d.filte(['x','y']).ndarray() -> ndarray([1,2]) 
# or any operations you can do with DefDict
# You can set values and it'll be reflected to the original DefDict
d.filter('z').update(10) -> {'z': 10}
print(d) -> {'x': 1, 'y':2, 'z':10}
```

Other dict methods are implemented
```python
# you can use DefDict as if it is just a dictionary
d.values()
d.keys()
d.items()
d.update()      # same behavior as set()
d.setdefault()  # same behavior as update()
d.clear()       # also clear definitions
d.pop()         # re-initialize given key
d.popitem()     # re-initialize given key
```

DefDict has shallow and deep copy options:
```python
# shallow copy
d_shallow = d.copy()  # the same as dict.copy() behavior
# deep copy
d_deep = d.clone()    # not in dict
```
## Print
You can see the contents by simply doing
```python
print(d) -> {'x': 1, 'y':2, 'z':3}
```

## Object-oriented: Prefixing/Suffixing and nested DefDict
### Prefixing
You want keys to be descriptive and using numbers as a key is not so great. So you can prefix the keys like
```python
print(d_j)  -> {'j.0': 1, 'j.1': 2,'j.2': 3}       # joint 0, 1, 2
# or 
print(d_ID) -> {'ID.11': 1, 'ID.12': 2,'ID.13': 3}    # Motor ID 11, 12,  13
```
But this is difficult to use programmatically because you always need to create a key. This is why DefDict has prefixing:
```python
d_j = DefDict({'j.0': 1, 'j.1': 2,'j.2': 3}, prefixes='j')
d_j.j() = {'0': 1, '1': 2,'2': 3}
# or you can specify a sub set of them
d_j.j([1,2]) = {'1': 2,'2': 3}
d_j.j(1) = {'1': 2}
```

```python
d_ID = DefDict({'ID.11': 1, 'ID.12': 2,'ID.13': 3}, prefixes=['ID']) # you can hand over list of prefixes
d_ID.ID() = {'11': 1, '12': 2,'13': 3}
# or you can specify a sub set of them
d_ID.ID([11,12]) = {'11': 2,'12': 3}
d_ID.ID(11) = {'11': 2}
```

### Suffixing
A similar thing is possible for the key itself
```python
d = DefDict({'pos': 1, 'vel':2, 'acc':3}, suffixes=['pos', 'vel', 'acc'])
d.pos -> 1
d.vel -> 2
d.acc -> 3
```
But this is more useful when DefDict is nested

## Nested DefDict
You can nest DefDict, but you can easily get or set the values using prefixing and suffixing:
```python
DEF = {'pos': 1, 'vel':2, 'acc':3}
d_j = DefDict({'j.0': DefDict(DEF), 'j.1': DefDict(DEF),'j.2': DefDict(DEF)}, prefixes='j', suffixes=DEF) # DEF is dict and only keys are used
print(d_j)  -> {'j.0': {'pos': 1, 'vel':2, 'acc':3}, 'j.1': {'pos': 1, 'vel':2, 'acc':3},'j.2': {'pos': 1, 'vel':2, 'acc':3}}
```
This would be very informative, but very difficult to deal with. But using suffixing:
```python
d_j.pos()      -> {'j.0': 1, 'j.1': 1,'j.2': 1}
d_j.j().pos()  -> {'0': 1, '1': 1,'2': 1}
d_j.j(2).pos() -> {'2': 1}
d_j.j(0)       -> {'j.0': {'pos': 1, 'vel':2, 'acc':3}}
# You can use any method in DefDict in addition to suffixing
d_j.j().vel().list() -> [2,2,2]
```

Of course, you can set values in the same way and the original structure also gets updated:
```python
d_j.j().pos().update([4,5,6]) -> {'0': 4, '1': 5,'2': 6}
print(d_j)             -> {'j.0': {'pos': 4, 'vel':2, 'acc':3}, 'j.1': {'pos': 5, 'vel':2, 'acc':3},'j.2': {'pos': 6, 'vel':2, 'acc':3}}
```

## 2D array to Nested DefDict
You can set nested DefDict values at a time as follows:
```python
array_2d = [[11,12,13], [4,5,6]]
array_2d = [{'pos': 11, 'vel':12, 'acc':13}, {'pos': 4, 'vel':5, 'acc':6}]
array_2d = [np.array([11,12,13]), np.array([4,5,6])]
array_2d = np.array([[11,12,13],[4,5,6]])
d_j.update(array_2d)   ->  {'j.0': {'pos': 11, 'vel':12, 'acc':13}, 'j.1': {'pos': 4, 'vel':5, 'acc':6},'j.2': {'pos': 1, 'vel':2, 'acc':3}}
```
As long as both the top level and the sub-level are compatible with DefDict, any combinations should work. 
Top level DefDict calls the sub-level DefDict.update() internally.

# Math Operation
DefDict is to support basic math operations for convenience, unlike dictionaries. Still, complex math should be done through such as numpy for efficiency. 
You can check [#79](https://github.com/Suke0811/AbstractedRobot/issues/79) for the latest available math operations for DefDict

**Not available for nested DefDict yet.**

```python
pos = DefDict(dict(x=0,y=0,z=0))
another_pos = pos.clone().update([1,1,1])
pos + another_pos -> {'x': 1, 'y': 1,'z': 1}
```
or
```python
pos + [1,1,1] -> {'x': 1, 'y': 1,'z': 1}
```
or
```python
pos + 1 -> {'x': 1, 'y': 1,'z': 1}
```

```python
pos = DefDict(dict(x=1,y=2,z=3))
pos_rot = DefDict((dict(x=1,y=2,z=3),
                   dict(qx=0,qy=0,qz=0, qw=1))) # Tuple of two dicts
pos_rot += pos -> {'x': 2, 'y': 4,'z': 6, 'qx': 0,'qy': 0,'qz': 0, 'qw': 1}
pos += pos_rot -> {'x': 2, 'y': 4,'z': 6}
```
You can of course use other DefDict methods in combination
```python
pos_rot.filter(pos) + 1 -> {'x': 2, 'y': 3,'z': 4, 'qx': 0,'qy': 0,'qz': 0, 'qw': 1}
```

## Iterator
```python
print(d_j)  -> {'j.0': {'pos': 4, 'vel':2, 'acc':3}, 'j.1': {'pos': 5, 'vel':2, 'acc':3},'j.2': {'pos': 6, 'vel':2, 'acc':3}}
for val in d_j: # or for val in d_j.value()
    print(val)
>> {'pos': 4, 'vel':2, 'acc':3}
>> {'pos': 5, 'vel':2, 'acc':3}
>> {'pos': 6, 'vel':2, 'acc':3}
```
You can use prefix/sufix 
```python
for val in d_j.pos():
    print(val)
>> 4
>> 5
>> 6
```

## Performance Notes
Recent benchmark using `pytest-benchmark` shows nested DefDict operations run about 1.37x faster after the latest optimizations (from ~91.5µs to ~66.9µs per run).
