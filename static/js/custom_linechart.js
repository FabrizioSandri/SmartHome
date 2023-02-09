class Custom extends Chart.LineController {
    draw() {
        super.draw(arguments);
        
        const ctx = this.chart.ctx;
        
        if (this.chart.tooltip._active && this.chart.tooltip._active.length) {

            var activePoint = this.chart.tooltip._active[0];

            var x = activePoint.element.x;
            
            var keys = Object.keys(this.chart.scales);
            var y_key = keys.find(function (el) {
                return el.startsWith("y");
            });
            
            var topY = this.chart.scales[y_key].top;
            var bottomY = this.chart.scales[y_key].bottom;
            
            // draw line
            ctx.save();
            ctx.beginPath();
            ctx.moveTo(x, topY);
            ctx.lineTo(x, bottomY);
            ctx.lineWidth = 2;
            ctx.strokeStyle = 'rgba(138, 138, 138, 0.7)';
            ctx.stroke();
            ctx.restore();
        }
    }
};

Custom.id = 'custom_line';
Custom.defaults = Chart.LineController.defaults;
Chart.register(Custom);