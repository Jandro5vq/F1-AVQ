var myChart;

function GP(data){
    var table = new Tabulator("#results-table", {
        data:data,
        columns:[
            {title:"Position", field:"Pos", hozAlign:"center", resizable:false},
            {title:"Col", field:"Color", formatter:"color", hozAlign:"center", resizable:false},
            {title:"Abbreviation", field:"Abv", hozAlign:"center", headerSort:false, resizable:false},
            {title:"FullName", field:"Name", hozAlign:"center", headerSort:false, resizable:false},
            {title:"Points", field:"Points", hozAlign:"center", headerSort:false, resizable:false},
            {title:"Status", field:"Status", hozAlign:"center", headerSort:false, resizable:false},
        ],
    });
}

function GDrivTable(){
    var table = new Tabulator("#results-table", {
        data:GDrivRes,
        columns:[
            {title:"Position", field:"Pos", hozAlign:"center", resizable:false},
            {title:"Col", field:"Color", formatter:"color", hozAlign:"center", resizable:false},
            {title:"Abbreviation", field:"Abv", hozAlign:"center", headerSort:false, resizable:false},
            {title:"FullName", field:"Name", hozAlign:"center", headerSort:false, resizable:false},
            {title:"Points", field:"Points", hozAlign:"center", headerSort:false, resizable:false},
        ],
    });
}

function GConTable(){
    var table = new Tabulator("#results-table", {
        data:GConRes,
        columns:[
            {title:"Position", field:"Pos", hozAlign:"center", vertAlign:"middle", resizable:false},
            {title:"Col", field:"Color", formatter:"color", vertAlign:"middle", hozAlign:"center", resizable:false},
            {title:"Abbreviation", field:"Name", hozAlign:"center", vertAlign:"middle", headerSort:false, resizable:false},
            {title:"Points", field:"Points", hozAlign:"center", vertAlign:"middle", headerSort:false, resizable:false},
            {title:"", field:"img", formatter:"image", headerSort:false, resizable:false, formatterParams:{ height:"45px", width:"50px", urlPrefix:"/static/img/TeamLogos/" }},
            {title:"", field:"img", formatter:"image", headerSort:false, resizable:false, formatterParams:{ height:"45px", width:"152px", urlPrefix:"/static/img/Car/" }},
        ],
    });
}

function drawFastLapChart(dt){

    var ctx = document.getElementById('Chart');

    if (myChart) {
        myChart.destroy();
    }

    sortDT = dt.sort((a, b) => {
        if (a.LapTime < b.LapTime) {
            return -1;
        }
    });
    
    var title = "Fastest lap of each driver"
    
    Chart.defaults.borderColor = '#3f3f3f';
    Chart.defaults.color = '#f5f5dc';
    Chart.defaults.font.family = "'Space Grotesk', sans-serif"
    
    function millisecondsToTime(milli) {
        var milliseconds = milli % 1000;
        var seconds = Math.floor((milli / 1000) % 60);
        var minutes = Math.floor((milli / (60 * 1000)) % 60);
        return minutes + ":" + seconds + "." + milliseconds;
    }
    
    myChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: sortDT.map(row => row.Abv),
            datasets: [{
                data: sortDT.map(row => row.LapTime),
                backgroundColor: sortDT.map(row => row.Color),
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: false,
                    ticks: {
                        callback: function (value, index, ticks) {
                            lab = millisecondsToTime(value)
                            return lab;
                        }
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        title: function(tooltipItem, data) {
                            return sortDT[tooltipItem[0]['dataIndex']]['Name'];
                        },
                        label: function(tooltipItem, data) {
                            return 'Time: ' + millisecondsToTime(sortDT[tooltipItem['dataIndex']]['LapTime']);
                        }
                    }
                },
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: title,
                    font: {
                        size: 20
                    }
                }
            }
        }
    });
}

function labelCheck(element){
    if ('Abv' in element) {
        return element.Abv
    }
    else{
        return element.Name
    }
}

function drawPtsPerGP(dt){

    var ctx = document.getElementById('Chart');

    if (myChart) {
        myChart.destroy();
    }

    set = [];

    dt.forEach(element => {
        set.push(
            {
                label: labelCheck(element),
                borderColor: element.Color,
                backgroundColor: element.Color,
                data: Object.values(element).slice(0,23)
            }
        )
    });
    
    var title = "Points in each GP"
    
    Chart.defaults.borderColor = '#3f3f3f';
    Chart.defaults.color = '#f5f5dc';
    Chart.defaults.font.family = "'Space Grotesk', sans-serif"
    
    myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [1,2],
            datasets: set
        },
        options: {
            scales: {
                y: {
                    beginAtZero: false
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        title: function(tooltipItem, data) {
                            return dt[tooltipItem[0]['datasetIndex']]['Name'];
                        },
                        label: function(tooltipItem, data) {
                            return "  " + dt[tooltipItem['datasetIndex']][tooltipItem['dataIndex'] + 1] + " Points";
                        }
                    }
                },
                legend: {
                    display: true,
                    position: 'bottom'
                },
                title: {
                    display: true,
                    text: title,
                    font: {
                        size: 20
                    }
                }
            }
        }
    });
}

async function TableUpdate(){
    switch (document.getElementById("Result-id").value) {
        case "ds":
            // % ========== TITULO ==========
            document.getElementById('Title').innerText = "Driver Standings";
            var LeftIMG = document.getElementById('Left-img');
            LeftIMG.src = "/static/img//SteeringWheel.svg";
            LeftIMG.className = 'svg-img';
            var RightIMG = document.getElementById('Right-img');
            RightIMG.src = "/static/img//SteeringWheel.svg";
            RightIMG.className = 'svg-img';
            // % ========== PODIO ==========
            for (let i = 0; i < 3; i++) {
                img = await getDimg(GDrivRes[i]['Name'])
                id = 'p' + String(i+1) + 'img'
                document.getElementById(id).src = '/static/img/Driver/' + img
            }
            // % ========== GRAFICO ==========
            drawPtsPerGP(ResPerGP);
            // % ========== TABLA ==========
            GDrivTable();
        break;

        case "cs":
            // % ========== TITULO ==========
            document.getElementById('Title').innerText = "Constructor Standings";
            var LeftIMG = document.getElementById('Left-img');
            LeftIMG.src = "/static/img/Wrench.svg";
            LeftIMG.className = 'svg-img';
            var RightIMG = document.getElementById('Right-img');
            RightIMG.src = "/static/img/Wrench.svg";
            RightIMG.className = 'svg-img';
            // % ========== PODIO ==========
            for (let i = 0; i < 3; i++) {
                id = 'p' + String(i+1) + 'img'
                document.getElementById(id).src = '/static/img/TeamLogos/' + GConRes[i]['img']
            }
            // % ========== GRAFICO ==========
            drawPtsPerGP(TeamResPerGP);
            // % ========== TABLA ==========
            GConTable();
        break;

        default:
            // % ========== DATOS ==========
            var n = document.getElementById("Result-id").value
            if (n == "lastgp") {
                n = EndedGP.length
            }
            const GPR = await getGPRes(n);
            const GPD = await getGPDat(n);
            // % ========== TITULO ==========
            document.getElementById('Title').innerText = GPD[0]['Name'];
            var LeftIMG = document.getElementById('Left-img');
            LeftIMG.src = String("/static/img/Flags/" +  GPD[0]['Flag']);
            LeftIMG.className = 'Flag-img';
            var RightIMG = document.getElementById('Right-img');
            RightIMG.src = String("/static/img/Circuit/" +  GPD[0]['Circuit']);
            RightIMG.className = 'Circuit-img';
            // % ========== PODIO ==========
            for (let i = 0; i < 3; i++) {
                img = await getDimg(GPR[i]['Name'])
                id = 'p' + String(i+1) + 'img'
                document.getElementById(id).src = '/static/img/Driver/' + img
            }
            // % ========== GRAFICO ==========
            var GPFL = await getGPFL(n);
            drawFastLapChart(GPFL)
            // % ========== TABLA ==========
            GP(GPR);
        break;
    }
}

async function getDimg(name){
    const DL = await getDList();
    for (var i = 0; i < DL.length; i++){
        if (DL[i]['Name'] == name){
            return DL[i]['img']
        }
    }
}

TableUpdate(EndedGP.length);
