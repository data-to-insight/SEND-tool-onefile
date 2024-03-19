function run_analysis () {
    const files = csvFile.files;
    const csv_array = []
     Object.keys(files).forEach(i => {
       const file = files[i];
       const reader = new FileReader();
       reader.onload = (e) => {
       const text = e.target.result
       csv_array.push(text)
    };
    reader.readAsText(file);
    window.files = csv_array
   })
   
   async function run_python() {
     let pyodide = await loadPyodide();
     await pyodide.loadPackage(["pandas", "micropip"]);
     
     // load initial python packages
     await pyodide.runPythonAsync(` 
     import micropip
     await micropip.install('plotly==5.0.0')
     `)

     // run main Python script
     await pyodide.runPythonAsync(await (await fetch("https://raw.githubusercontent.com/WillLP-code/pyodide-test/main/python_app.py")).text());
     pyodide.globals.get("fig")
   
   // document.getElementById("print").disabled = false
     let plotly = document.getElementById("plotly-output")
     render_plot(plotly, document.fig)
   }

   function render_plot(container, plot_html) {
     let range = document.createRange();
     range.selectNode(container);
     let documentFragment = range.createContextualFragment(plot_html);
     while (container.hasChildNodes()) {  
       container.removeChild(container.firstChild);
     }
     container.appendChild(documentFragment);
     container.className = "plotly";
     $(".spinner").addClass('d-none');
   };

   run_python();  
   
 }  


 async function pdfFunction () {
    console.log('stuff is happening')

    var source = window.document.getElementsByTagName("plotly-output");
    var doc = new jsPDF();

    doc.html('some text', {
      callback: function (doc) {
        // doc.save();
      },
      x: 10,
      y: 10
    });

    doc.output("dataurlnewwindow");
  }