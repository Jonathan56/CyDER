CyderAPI
======

Javascript module to interact with the CyDER REST API.

It is asynchronous and use promises to be used easily with await.  
An authorization token is needed to use the API. It can be requested with `auth()`. `auth()` should be call before any other request to the API but no need to await for it before using the API: if `auth()` is called and a request is made before the token arrive, the request will wait for the token.

`auth([username, password])`:  
`username` optional string  
`password` optional string  
Request the authentication token needed to use the rest API using the id provided
If no username is provided, the session cookie is used.
Return a promise that resolve when the token is received.

`rest(method, url[, content[, contentType]])`:  
`method`: string, HTTP method to use (ie `'POST'`, `'GET'`...)  
`url`: string, URL of the request  
`content`: optional, content of the request  
`contentType`: optional string, mime type of the content of the request. If omitted, `application/json` is used and content is stringified to json.  
Make a request to the REST API. More specific methods of the module should be preferred to this one.

`class Res` is a class to be used in mirror of Models&ModelViewSet&Routers in Django&DjangoRestFramework. It allow to manipulate a Resource using the REST API. Provide methods `getAll()` (mirror for a list view) and `get()` (mirror for a detail view). The data are cached: when unknown it return a promise which resolve with the data requested, otherwise it return directly the data.  
To use it you have to build an instance of the `Res` class for each type of resources you want to manage: `let MyResource = new Res(url, lookup)`. `url` is the url of the REST API endpoint, lookup is the name of the lookup variable for the `get` function.  
By default the class `Res` only provide function for read only. If your endpoint allow modification an deletion you can extend the class using Mixins `Res.WriteMixin` and `Res.DeleteMixin`. You can compose Mixins like so:
```
let ReadWriteDeleteRes = Res.DeleteMixin(Res.WriteMixin(Res));
let MyResource = new ReadWriteDeleteRes(url, lookup);
```
If your endpoint allow other action you can extends the `Res` class (see `ProjectRes` in api.js).  
Because data are cached you should be careful when modifying data return by one of those get values: an other get could return the modified values (example: `let map = MyResource.getAll(); map.delete(somekey);` this change the cached value. The next `getAll()` will return a map with the entry of `somekey` deleted. The use of `getAll(true)` will restore it if the value is still on the server)


`Res.getAll([force])`  
`force` optional boolean: If `true`, cached value are not used. `false` by default  
Return a map of all instance of this Res, keyed by the value of their lookup.

`Res.get(lookup[, force])`  
`force` optional boolean: If `true`, cached value are not used. `false` by default  
Return the instance of this Res which have the specified lookup value.

`class NestedRes` is a class to be used in mirror of NestedRouter in DjangoRestFramework. Must be used as a Res but require to specified the lookup of the parent(s) before other parameters (example: Node is nested in Model so `Node.get(modelLookup, nodeLookup, force)`, if some Info was nested in Note `Info.get(modelLookup, nodeLookup, infoLookup, force)`...)
