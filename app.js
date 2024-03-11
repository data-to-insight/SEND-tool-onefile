(function () {

    // var input = document.getElementById('file');
    var input = document.getElementById('file');
    var table = document.getElementById('table');

    if (!input) {
        return;
    }

    input.addEventListener('change', function() {
        if (!!input.files && input.files.length > 0) {
            // implement toJSON() behavior  
            var input = input.files[0]
            input.toJSON = function() { return {
                'lastModified'     : myFile.lastModified,
                'lastModifiedDate' : myFile.lastModifiedDate,
                'name'             : myFile.name,
                'size'             : myFile.size,
                'type'             : myFile.type 
            };}  
            
            // then use JSON.stringify on File object
            input.stringify(input);
        }
    });
})();