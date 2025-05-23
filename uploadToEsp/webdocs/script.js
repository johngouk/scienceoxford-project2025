var firstTime = false;

function setDataValue(value)
{
    newData = JSON.parse(value);
    var mytab = document.getElementById("data");
    var row, title, val;
    for (let i=0; i<newData.length; i++)
    {
        if (firstTime) 
        {
            row = mytab.insertRow();
            title = row.insertCell(0);
            val = row.insertCell(1);
            title.innerHTML = Object.keys(newData[i])[0];
            val.innerHTML = Object.values(newData[i])[0];
        }  else 
         
        { // Look through the table rows to find the one with the same title
            for (let row of mytab.rows) 
            {
                if (row.cells[0].innerHTML === Object.keys(newData[i])[0]) 
                {
                    row.cells[1].innerHTML = Object.values(newData[i])[0];
                }
            }
        }
    }
    firstTime = false;
}

async function getText(file)
{
    let myObject = await fetch(file);
    let myText = await myObject.text();
    return myText;
}

gatherDataAjaxRunning = false;
function gatherData()
{
    // stop overlapping requests
    if(gatherDataAjaxRunning) return;
    
    //document.getElementById("demo").innerHTML = "gatherData";
    gatherDataAjaxRunning = true;

    getText("/data").then(
        function(value){setDataValue(value);}
    )

    gatherDataAjaxRunning = false;
}

var dataTimer;
function docLoaded()
{
    //set_rgb_colour(); // initialise rgb display
    //document.getElementById("demo").innerHTML = "Doc ready";
    dataTimer = setInterval(window.gatherData,1000); // call data every 0.5 seconds
}