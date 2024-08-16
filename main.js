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
    window.excel_file = csvFile.files
   })
   run_python();
}

async function run_python() {
    window.postcode_data = $.getJSON('https://raw.githubusercontent.com/thomasvalentine/Choropleth/main/Local_Authority_Districts_(December_2021)_GB_BFC.json', function(data) {
      return data
    });


    let pyodide = await loadPyodide();
    await pyodide.loadPackage(["pandas", "micropip"]);
    
    // load initial python packages
    await pyodide.runPythonAsync(` 
    import micropip
    await micropip.install('plotly==5.0.0')
    await micropip.install('openpyxl')
    import openpyxl
    import xml.etree.ElementTree as ET

    import pandas as pd
    import js
    import pyodide_js
    import json
    import io
    import plotly.express as px
    import plotly.graph_objects as go
    import numpy as np
    import openpyxl

    import warnings
    from pandas.core.common import SettingWithCopyWarning

    warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)

    input_type = None

    try:
        from js import files, refDateVal
    except:
        js.alert("Did you upload the correct files, more info in the instructions.")

    dfs = {}

    #if len(files) != 5:
    #    js.alert("Wrong number of files uploaded, expected 5. See the 'About' page for more info.")
    
    if len(files) > 1:
        for i, v in enumerate(files):
            dfs[i] = pd.read_csv(io.StringIO(files[i]))
            js.console.log("csvs sucessfully read")
            input_type = 'csv'
            js.console.log('input type csv')
    elif len(files) == 1:
        
        dta = files[0]
        # js.console.log(dta)
        try:
            root = ET.fromstring(dta)
            input_type = 'xml'
            js.window.input_type = input_type
            js.console.log('input type xml')
        except:
            js.alert("Did you upload the correct files, more info in the instructions.")
    else:
        js.alert("Did you upload the correct files, more info in the instructions.")

    `)

    console.log(window.input_type)
    // run main Python script
    await pyodide.runPythonAsync(await (await fetch('https://raw.githubusercontent.com/data-to-insight/SEND-tool/main/python_app.py')).text());
    pyodide.globals.get("fig")

// document.getElementById("print").disabled = false

    // Totals plots
    let total_gender = document.getElementById("total_gender")
    render_plot(total_gender, document.total_gender_hist)

    let total_age = document.getElementById("total_age")
    render_plot(total_age, document.total_age_hist)

    let total_ethnicity = document.getElementById("total_ethnicity")
    render_plot(total_ethnicity, document.total_ethnicity_hist)

    let total_count = document.getElementById("total_count")
    render_plot(total_count, document.total_count_indicator)

    // ehc ceased plots
    let ehc_ceased = document.getElementById("ehc_ceased")
    render_plot(ehc_ceased, document.ehc_ceased_indicator)

    let ehc_ceased_gender = document.getElementById("ehc_ceased_gender")
    render_plot(ehc_ceased_gender, document.ehc_ceased_gender_hist)

    let ehc_ceased_ethnicity = document.getElementById("ehc_ceased_ethnicity")
    render_plot(ehc_ceased_ethnicity, document.ehc_ceased_ethnicity_hist)

    let ehc_ceased_age = document.getElementById("ehc_ceased_age")
    render_plot(ehc_ceased_age, document.ehc_ceased_age_hist)

    let ehc_ceased_reason = document.getElementById("ehc_ceased_reason")
    render_plot(ehc_ceased_reason, document.ehc_ceased_reason_pie)

    // ehc started plots
    let ehc_started = document.getElementById("ehc_started")
    render_plot(ehc_started, document.ehc_started_indicator)

    let ehc_started_gender = document.getElementById("ehc_started_gender")
    render_plot(ehc_started_gender, document.ehc_started_gender_hist)

    let ehc_started_ethnicity = document.getElementById("ehc_started_ethnicity")
    render_plot(ehc_started_ethnicity, document.ehc_started_ethnicity_hist)

    let ehc_started_age = document.getElementById("ehc_started_age")
    render_plot(ehc_started_age, document.ehc_started_age_hist)

    // ass completed plots
    let ass_completed = document.getElementById("ass_completed")
    render_plot(ass_completed, document.ass_completed_indicator)

    let ass_completed_gender = document.getElementById("ass_completed_gender")
    render_plot(ass_completed_gender, document.ass_completed_gender_hist)

    let ass_completed_ethnicity = document.getElementById("ass_completed_ethnicity")
    render_plot(ass_completed_ethnicity, document.ass_completed_ethnicity_hist)

    let ass_completed_age = document.getElementById("ass_completed_age")
    render_plot(ass_completed_age, document.ass_completed_age_hist)

    let ass_completed_reason = document.getElementById("ass_completed_reason")
    render_plot(ass_completed_reason, document.ass_completed_reason_pie)    

    // ehc started plots
    let open_ass = document.getElementById("open_ass")
    render_plot(open_ass, document.ass_open_timeframe_indicator)

    let open_ass_gender = document.getElementById("open_ass_gender")
    render_plot(open_ass_gender, document.ass_open_timeframe_gender_box)

    let open_ass_ethnicity = document.getElementById("open_ass_ethnicity")
    render_plot(open_ass_ethnicity, document.ass_open_timeframe_ethnicity_box)

    let open_ass_age = document.getElementById("open_ass_age")
    render_plot(open_ass_age, document.ass_open_timeframe_age_box)

    // closed ass timeframes
    let ass_closed_timeframe_gender = document.getElementById("ass_closed_timeframe_gender")
    render_plot(ass_closed_timeframe_gender, document.ass_closed_timeframe_gender_box)

    let ass_closed_timeframe_age = document.getElementById("ass_closed_timeframe_age")
    render_plot(ass_closed_timeframe_age, document.ass_closed_timeframe_age_box)

    let ass_closed_timeframe_ethnicity = document.getElementById("ass_closed_timeframe_ethnicity")
    render_plot(ass_closed_timeframe_ethnicity, document.ass_closed_timeframe_ethnicity_box)

    // request breakdowns
    let req_count = document.getElementById("req_count")
    render_plot(req_count, document.req_count_indicator)

    let req_gender = document.getElementById("req_gender")
    render_plot(req_gender, document.req_gender_box)

    let req_age = document.getElementById("req_age")
    render_plot(req_age, document.req_age_box)

    let req_ethnicity = document.getElementById("req_ethnicity")
    render_plot(req_ethnicity, document.req_ethnicity_box)
   
    // multiple appearances
    let multiple_m2_div = document.getElementById("multiples_m2_div")
    render_plot(multiple_m2_div, document.multiple_m2)

    let multiple_m3_div = document.getElementById("multiples_m3_div")
    render_plot(multiple_m3_div, document.multiple_m3)

    // journeys
    let journeys_div = document.getElementById("journeys_div")
    render_plot(journeys_div, document.journeys)

    // Open plan lengths
    let open_plan_length_gender = document.getElementById("open_plan_length_gender")
    render_plot(open_plan_length_gender, document.open_plan_length_gender_hist)

    let open_plan_length_age = document.getElementById("open_plan_length_age")
    render_plot(open_plan_length_age, document.open_plan_length_age_hist)

    let open_plan_length_ethnicity = document.getElementById("open_plan_length_ethnicity")
    render_plot(open_plan_length_ethnicity, document.open_plan_length_ethnicity_hist)

    // Closed plan lengths
    let closed_plan_length_gender = document.getElementById("closed_plan_length_gender")
    render_plot(closed_plan_length_gender, document.closed_plan_length_gender_hist)

    let closed_plan_length_age = document.getElementById("closed_plan_length_age")
    render_plot(closed_plan_length_age, document.closed_plan_length_age_hist)

    let closed_plan_length_ethnicity = document.getElementById("closed_plan_length_ethnicity")
    render_plot(closed_plan_length_ethnicity, document.closed_plan_length_ethnicity_hist)


    // show plot titles
    $("#total_header").removeClass('d-none');
    $("#ehc_ceased_header").removeClass('d-none');
    $("#ehc_started_header").removeClass('d-none');
    $("#ass_completed_header").removeClass('d-none');
    $("#open_ass_timeframe_header").removeClass('d-none');
    $("#ass_closed_timeframe_header").removeClass('d-none');
    $("#request_header").removeClass('d-none');
    $("#multiple_appearances_header").removeClass('d-none');
    $("#journeys_header").removeClass('d-none');
    $("#open_plan_length_header").removeClass('d-none');
    $("#closed_plan_length_header").removeClass('d-none');
    


    $("#myForm").addClass('d-none');

    $("#print").removeClass('d-none'); 
    
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
    $("#submitSpinner").addClass('d-none');
};  

//  async function pdfFunction () {
//     console.log('stuff is happening')

//     var source = window.document.getElementsByTagName("plotly-output");
//     var doc = new jsPDF();

//     doc.html('some text', {
//       callback: function (doc) {
//         // doc.save();
//       },
//       x: 10,
//       y: 10
//     });

//     doc.output("dataurlnewwindow");
//  }