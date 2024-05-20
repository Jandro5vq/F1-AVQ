function nextGP(){
    var today = new Date()
    for (let x = 0, cont = true; x < Schedule.length && cont == true; x++) {
        var GPDate = new Date(LocalGPTime(Schedule[x].ID));
        if (today < GPDate) {
            cont = false;
            document.getElementById('GPName').innerText = Schedule[x].Name;
            return Schedule[x];
        };
    }
};

async function getBet(){
    var GPNum = nextGP().ID
    var bet = await getActualBet(GPNum)
    bet.forEach((element, index) => {
        var selector = document.getElementById(index);
        selector.value = String(element.Abv)
        UpdateIMG(index)
    });
}

function UpdateIMG(id){
    n = document.getElementById(id).value;
    imgid = 'img' + String(id);
    img = document.getElementById(imgid);
    for (let x = 0; x < Dlist.length; x++){
        if (n == Dlist[x]['Abv']) {
            img.src = `/static/img/Driver/${Dlist[x]['img']}`;
        }
    }
};

function Submit(){
    bet = [];
    obj = {User: CurrentUser, GP:nextGP().ID};
    bet.push(obj);
    for (let x = 0; x < 10; x++) {
        n = document.getElementById(x).value;
        obj = {pos: x+1, Name: n};
        bet.push(obj);
    }
    const request = new XMLHttpRequest();
    request.open('POST', `/SubmitBet/${JSON.stringify(bet)}`);
    request.send();
};

function Rank(data){
    var table = new Tabulator("#UserTable", {
        data:data,
        columns:[
            {title:"Position", field:"Pos", hozAlign:"center", resizable:false},
            {title:"Name", field:"Name", hozAlign:"center", headerSort:false, resizable:false},
            {title:"Points", field:"Points", hozAlign:"center", headerSort:false, resizable:false}
        ],
    });
    
    data.forEach(element => {
        if (element.Name.toUpperCase() == CurrentUser.toUpperCase()) {
            document.getElementById('pos').innerText = "Your actual position is:  " + element.Pos
        }
    });
};

Schedule.forEach(element => {
    var UTCtoday = new Date().toUTCString();
    
    if (UTCtoday < element.Date) {
        
    }
});

function LocalGPTime(GPNum){
    var D = moment.tz(Schedule[GPNum - 1]['Date'], Schedule[GPNum - 1]['Timezone']);
    return D.tz(moment.tz.guess()).format();
};


var countDownDate = new Date(LocalGPTime(nextGP().ID)).getTime();

// Update the count down every 1 second
var x = setInterval(function() {
    // Get today's date and time
    var now = new Date().getTime();

    // Find the distance between now and the count down date
    var distance = countDownDate - now;

    // Time calculations for days, hours, minutes and seconds
    var days = Math.floor(distance / (1000 * 60 * 60 * 24));
    var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
    var seconds = Math.floor((distance % (1000 * 60)) / 1000);

    // Display the result in the element with id="demo"
    document.getElementById("Time").innerHTML = days + "d " + hours + "h "
    + minutes + "m " + seconds + "s ";

    // If the count down is finished, write some text
    if (distance < 0) {
        clearInterval(x);
        document.getElementById("Time").innerHTML = "EXPIRED";
    }
}, 1000);


Rank(UserList);
getBet();