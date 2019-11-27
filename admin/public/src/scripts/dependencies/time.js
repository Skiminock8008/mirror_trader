let CTX_TIME = {
    get_day: function(numeral) {
        switch(numeral) {
            case 0:
                return "Sunday"
            case 1:
                return "Monday"
            case 2:
                return "Tuesday"
            case 3:
                return "Wednesday"
            case 4:
                return "Thursday"
            case 5: 
                return "Friday"
            case 6:
                return "Saturday" 
        }
    },
    
    get_time: function () {
        let date = new Date();
        let day = date.getDay();
        let hour = date.getHours();
        let minute = date.getMinutes();
        let seconds = date.getSeconds();
        if (parseInt(seconds) < 10) {
            seconds = "0" + seconds;
        }
        return this.get_day(day) + " " + hour + ":" + minute + ":" + seconds;
    }
}