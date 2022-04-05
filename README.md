
# FB APP

This app readily uses cookies meaning once you login your cookies are saved and used until it expires.
To *login* first create an object for FB class
```  
x = FB() 
x.HandleSession("username","password")
```
Now it will tell you if you were successfully able to login or failed the attempt.
### To get own name 
This will return you own profile name
```
print(x.get_own_name())
```
### To get all pages you are admin in
This will return a dictionary of your pages name and its coresponding username.
```
print(x.getPagesList())
```
#### RESULT:
```
{'Test': 'Test-107071288636127'}
```
This username `Test-107071288636127` is essential to use post function of the script.

### Post using your own profile
#### Text
```
x.self_post("CAPTION GOES HERE")
```
#### Image 
```
x.self_image_post("Caption goes here","images.png")
```
### Post using your Page
Reemember we obatined our page username now it is required here. Function call is same as for own profile just provide for_ vale as your page username
 #### Text
 ```
 x.self_post("CAPTION GOES HERE",for_="Test-107071288636127")
 ```
 #### Image
 ```
 x.self_image_post("CAPTION GOES HERE","images.png",for_="Test-107071288636127")
 ```