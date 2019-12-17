package main;

import java.io.File;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.List;
import java.util.stream.IntStream;

public class FileCreator {

    private static final String COL_SEPARATOR = ",";
    private static final String PLAYER_NAME_COL_NAME = "Name";
    private static final String PLAYER_TEAM_COL_NAME = "Team";
    private static final String PLAYER_ROLE_COL_NAME = "Role";
    private static final String MATCHDAY_COL_NAME = "Matchday";
    private static final String VOTE_COL_NAME = "Vote";

    private final List<Player> playerList;

    public FileCreator(final List<Player> playerList){
        this.playerList = playerList;
        this.indexedVoteSeries();
    }

    private void indexedVoteSeries() {
        File file = new File("Serie_storiche_indicizzate.txt");
        try {
            file.createNewFile();
            PrintWriter pw = new PrintWriter(file, "UTF-8");

            // Header
            pw.println(PLAYER_NAME_COL_NAME + COL_SEPARATOR
                     + PLAYER_TEAM_COL_NAME + COL_SEPARATOR
                     + PLAYER_ROLE_COL_NAME + COL_SEPARATOR
                     + MATCHDAY_COL_NAME + COL_SEPARATOR
                     + VOTE_COL_NAME
            );

            // Body
            this.playerList.stream()
                    .peek(Player::fillMissingSerieValues)
                    .forEach(p ->
                IntStream.range(1,39).forEach(day ->
                    pw.println(p.getName() + COL_SEPARATOR
                             + p.getTeam() + COL_SEPARATOR
                             + p.getRole() + COL_SEPARATOR
                             + day + COL_SEPARATOR + " "
                             + p.getSortedVoteForMatchdayForFile().get(day-1).getValue()
                    )
                )
            );
            pw.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
