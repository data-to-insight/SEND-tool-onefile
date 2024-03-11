    function getFiles(){
        var files = document.getElementById("file");
        var myArray = [];
        var file = {};
    
        console.log(files); // see the FileList
    
        // manually create a new file obj for each File in the FileList
        for(var i = 0; i < files.length; i++){
    
          file = {
              'lastMod'    : files[i].lastModified,
              'lastModDate': files[i].lastModifiedDate,
              'name'       : files[i].name,
              'size'       : files[i].size,
              'type'       : files[i].type,
          } 
    
          //add the file obj to your array
          myArray.push(file)
        }
    
        //stringify array
        console.log(JSON.stringify(myArray));
    }
