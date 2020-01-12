package main;

import java.io.File;
import java.io.IOException;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
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

    public FileCreator(final List<Player> playerList) {
        this.playerList = playerList;
        //this.saveIndexedVoteSeries();
    }

    private void printCsvHeaders(final PrintWriter pw) {
        pw.print(PLAYER_NAME_COL_NAME + COL_SEPARATOR
                + PLAYER_TEAM_COL_NAME + COL_SEPARATOR
                + PLAYER_ROLE_COL_NAME + COL_SEPARATOR);
        IntStream.range(1, Season.ALL_SEASONS_LENGTH + 1)
                .forEach(dayIndex -> pw.print(dayIndex + COL_SEPARATOR));
        pw.println();
    }


    public void saveIndexedVoteSeries() {
        File file = new File("serie_storiche_voti.csv");
        try (PrintWriter pw = new PrintWriter(file, StandardCharsets.UTF_8)) {
            file.createNewFile();
            // Header
            this.printCsvHeaders(pw);

            // Body
            this.playerList.stream()
                    .peek(Player::fillMissingVotesValues)
                    .forEach(p -> {
                        pw.print(p.getName() + COL_SEPARATOR
                                + p.getTeam() + COL_SEPARATOR
                                + p.getRole() + COL_SEPARATOR);
                        p.getVoteSeries().forEach((k, v) -> pw.print(v + COL_SEPARATOR));
                        pw.println();
                    });
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public void saveIndexedFantaVoteSeries() {
        File file = new File("serie_storiche_fantavoti.csv");
        try (PrintWriter pw = new PrintWriter(file, StandardCharsets.UTF_8)) {
            file.createNewFile();
            this.printCsvHeaders(pw);
            // Body
            this.playerList.stream()
                    .peek(Player::fillMissingFantaVotesValues)
                    .forEach(p -> {
                        pw.print(p.getName() + COL_SEPARATOR
                                + p.getTeam() + COL_SEPARATOR
                                + p.getRole() + COL_SEPARATOR);
                        p.getFantaVoteSeries().forEach((k, v) -> pw.print(v + COL_SEPARATOR));
                        pw.println();
                    });

        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
