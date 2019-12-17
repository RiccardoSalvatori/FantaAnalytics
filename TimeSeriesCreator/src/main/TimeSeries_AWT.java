package main;
/*
import org.jfree.chart.ChartFactory;
import org.jfree.chart.ChartPanel;
import org.jfree.chart.JFreeChart;
import org.jfree.data.time.TimeSeries;
import org.jfree.data.time.TimeSeriesCollection;
import org.jfree.data.time.Week;
import org.jfree.data.xy.XYDataset;
import org.jfree.ui.ApplicationFrame;

import java.util.ArrayList;
import java.util.List;


public class TimeSeries_AWT extends ApplicationFrame {

    private List<Player> playerList = new ArrayList<>();

    public TimeSeries_AWT(String title, List<Player> playerList) {
        super(title);
        this.playerList = playerList;
        this.init();
    }

    private void init() {
        final TimeSeries series = new TimeSeries("Serie Voti BERISHA", Week.class);
        int year = 2016;
        int week = 34;
        int i = 1;
        for(double elem : this.playerList.get(458).getVoteSeries()){
           series.add(new Week(week, new Integer(year)), elem);
           series.setRangeDescription(String.valueOf(week));
           if(i==38){
               week = 33;
               year = 2017;
           }
           i++;
           week++;
        }
        final XYDataset dataset = new TimeSeriesCollection(series);
        final JFreeChart chart = createChart( dataset );
        final ChartPanel chartPanel = new ChartPanel( chart );
        chartPanel.setPreferredSize( new java.awt.Dimension( 560 , 370 ) );
        chartPanel.setMouseZoomable( true , false );
        setContentPane(chartPanel);
    }

    private JFreeChart createChart(XYDataset dataset) {
        return ChartFactory.createTimeSeriesChart(
                "Computing Test",
                "Mese",
                "Fantavoto",
                dataset,
                false,
                false,
                false);

    }
}
*/