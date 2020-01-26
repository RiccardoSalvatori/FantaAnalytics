package main;

import java.io.*;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.util.function.Consumer;
import java.util.stream.Collectors;

import static main.Season.SEASON_LENGTH;


public class VotePicker {

    private static final String FILE_BASE_PATH = "resources/info_";
    private static final String FILE_EXTENSION = ".txt";
    private static final String VOTE_BASE_URL = "https://fantapiu3.com/fantacalcio-storico-voti-gazzetta-sport-";
    private static final String VOTE_PAGE_EXTENSION = ".php";
    private static final List<String> NO_VOTE = Arrays.asList("S.V.", "-");
    private final List<Player> allPlayers = new ArrayList<>();


    public VotePicker() {
        //new FileCreator(this.playerList);
    }

    public void initAllPlayers() {
        Season.getAllSeasons().forEach(season ->
                this.getPlayersFromFile(this.getInfoFromSite(season), season)
                        .forEach(player -> {
                            if (allPlayers.contains(player)) {
                                final Player p = allPlayers.get(allPlayers.indexOf(player));
                                player.getVoteSeries().forEach(p::addVote);
                                player.getFantaVoteSeries().forEach(p::addFantaVote);
                            } else {
                                allPlayers.add(new Player(player));
                            }
                        }));
    }

    public List<Player> getAllPlayers() {
        return Collections.unmodifiableList(this.allPlayers);
    }

    public void printPlayers() {
        this.allPlayers.forEach(System.out::println);
    }


    private File getInfoFromSite(Season season) {
        final File file =
                new File(new File(FILE_BASE_PATH + season.getSeasonName() + FILE_EXTENSION).getAbsolutePath());
        try {
            if (file.createNewFile()) {
                final PrintWriter pw = new PrintWriter(file, StandardCharsets.UTF_8);
                final URL url = new URL(VOTE_BASE_URL + season.getSeasonName() + VOTE_PAGE_EXTENSION);
                final Scanner s = new Scanner(url.openStream());
                boolean info = false;
                while (s.hasNext()) {
                    final String initLine = s.nextLine();
                    if (initLine.contains("<tbody")) {
                        info = true;
                    }
                    while (info) {
                        final String line = s.nextLine();
                        if (line.contains("</tbody>")) {
                            info = false;
                        } else {
                            pw.println(line);
                        }
                    }
                }
                pw.close();
            }
        } catch (IOException e) {
            e.printStackTrace();
        }

        return file;
    }

    private List<Player> getPlayersFromFile(File file, Season season) {
        List<Player> players = new ArrayList<>();
        try {
            BufferedReader br = new BufferedReader(new FileReader(file));
            while (true) {
                String initLine = br.readLine();
                if (initLine == null) {
                    break;
                } else {
                    if (initLine.toLowerCase().contains("giornata") && initLine.contains("<tr")) {
                        String day = initLine.substring(initLine.indexOf("GIORNATA") + 9,
                                initLine.indexOf(">") - 1);

                        String playerName = this.getTdContent(br.readLine());
                        String team = this.getTdContent(br.readLine());
                        br.readLine(); //commented td line
                        String role = this.getTdContent(br.readLine());
                        final String fv = this.getTdContent(br.readLine());
                        final String v = this.getTdContent(br.readLine());

                        if (!role.isEmpty()) {//empty role is for coaches

                                Player p = new Player(playerName, team, role);
                                int dayInt = Integer.parseInt(day) + season.getSeasonIndex() * SEASON_LENGTH;
                                double vDouble = NO_VOTE.contains(v) ? Player.DEFAULT_VOTE :
                                        Double.parseDouble(v.replace(',', '.'));
                                double fvDouble = NO_VOTE.contains(v) ? Player.DEFAULT_VOTE :
                                        Double.parseDouble(fv.replace(',', '.'));
                                Consumer<Player> updateVotes = player -> {
                                    player.addVote(dayInt, vDouble);
                                    player.addFantaVote(dayInt, fvDouble);
                                };
                                players.stream().filter(p::equals).findFirst().ifPresentOrElse(updateVotes, () -> {
                                    updateVotes.accept(p);
                                    players.add(p);
                                });

                        }
                    }
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return players;
    }

    /**
     * Return the content of html element td
     *
     * @param line string containing the html element
     */
    private String getTdContent(String line) {
        return line.substring(line.indexOf("<td>") + 4, line.indexOf("</td>"));
    }


}