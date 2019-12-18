// Modular Settings Page 
//old bg color: #EEDC82
//old resetTabs color: #c1c1c1
let TabSystem = {

    variables: {
        tabBars: document.querySelectorAll(".tab-bar a"),
        contents: document.querySelectorAll(".bp3-card"),
    },

    //Reset styling and add event listeners to add style once something is clicked
    init: function () {
        this.resetTabs();
        this.variables.contents[0].style = `display: flex;`;
        this.variables.tabBars[0].style = `background-color: #ad7580; color: #000 !important`;
        window.addEventListener('keydown', this.checkTab);

        this.variables.tabBars.forEach(function (tabBar, tabBarIndex) {
            tabBar.addEventListener("click", function () {
                TabSystem.resetTabs()
                TabSystem.variables.contents[tabBarIndex].style = `display: flex;`
                this.style = `background-color: #ad7580; color: #000; !important`
            })
        })
    },

    //Resets styling on all the elements
    resetTabs: function () {
        for (let i = 0; i < this.variables.contents.length; i++) {
            this.variables.contents[i].style = `display: none;`
            this.variables.tabBars[i].style = `background-color: #c1c1c1; color: #000 !important;`
        }
    },

    checkTab: function (e) {
        if (e.keyCode === 9) {
            for (let i = 0; i < TabSystem.variables.tabBars.length; i++) {
                TabSystem.variables.tabBars[i].classList.add('show-outline')
            }
        }
    }
}