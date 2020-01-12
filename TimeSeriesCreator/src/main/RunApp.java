package main;

public class RunApp {

    public static void main(String [ ] args){

        final VotePicker v = new VotePicker();
        v.initAllPlayers();
        new FileCreator((v.getAllPlayers())).saveIndexedVoteSeries();
        new FileCreator((v.getAllPlayers())).saveIndexedFantaVoteSeries();
    }
}
