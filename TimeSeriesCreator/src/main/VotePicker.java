package main;

import org.apache.poi.ss.usermodel.CellType;
import org.apache.poi.ss.usermodel.Row;
import org.apache.poi.xssf.usermodel.XSSFSheet;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;

import java.io.*;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.util.function.Consumer;
import java.util.function.Function;
import java.util.stream.Collectors;

import static main.Season.*;


public class VotePicker {

    private static final String FILE_BASE_PATH = "src/main/resources/info_";
    private static final String FILE_EXTENSION = ".txt";
    private static final String VOTE_BASE_URL = "https://fantapiu3.com/fantacalcio-storico-voti-gazzetta-sport-";
    private static final String VOTE_PAGE_EXTENSION = ".php";
    private static final String NO_VOTE = "S.V.";

    private final Set<Player> playersSeasonOne;
    private final Set<Player> playersSeasonTwo;
    private final Set<Player> playersSeasonThree;
    private final List<Pair<Integer,Double>> voteForMatchday;
    private final List<Pair<Integer,Double>> sortedVoteForMatchday;
    private final List<Integer> matchdays;
    private List<Integer> sortedMatchdays;


    public VotePicker() {
        //this.playerList = this.getPlayerList(SEASON_3);
        this.playersSeasonOne = this.getPlayersFromFile(this.getInfoFromSite(SEASON_1), SEASON_1 );
        this.playersSeasonTwo = this.getPlayersFromFile(this.getInfoFromSite(SEASON_2), SEASON_2);
        this.playersSeasonThree = this.getPlayersFromFile(this.getInfoFromSite(SEASON_3), SEASON_3);
        this.voteForMatchday = new ArrayList<>();
        this.sortedVoteForMatchday = new ArrayList<>();
        this.matchdays = new ArrayList<>();
        this.sortedMatchdays = new ArrayList<>();

        playersSeasonOne.forEach(System.out::println);
        playersSeasonTwo.forEach(System.out::println);
        playersSeasonThree.forEach(System.out::println);


        //all players that have played in all three seasons
                playersSeasonOne.stream()
                        .filter(playersSeasonTwo::contains)
                        .filter(playersSeasonThree::contains)
                        .map(p -> {
                            Function<Set<Player>,Player> getPlayerInSeason =
                                    season  -> season.stream().filter(p::equals).findFirst().get();
                            Player p1 = getPlayerInSeason.apply(this.playersSeasonOne);
                            Player p2 = getPlayerInSeason.apply(this.playersSeasonTwo);
                            Player p3 = getPlayerInSeason.apply(this.playersSeasonThree);

                            Player newPlayer = new Player(p1);
                            newPlayer.getVoteSeries().putAll(p2.getVoteSeries());
                            newPlayer.getVoteSeries().putAll(p3.getVoteSeries());

                            newPlayer.getFantaVoteSeries().putAll(p2.getFantaVoteSeries());
                            newPlayer.getFantaVoteSeries().putAll(p3.getFantaVoteSeries());
                            return newPlayer;
                        }).forEach(System.out::println);



        //new FileCreator(this.playerList);
    }

    private void makeVoteSeries(final File file) {
         this.playersSeasonOne.stream()
                 //.filter(player -> this.getVote(player, file))
                 .peek(player -> System.out.println("Created serie for: " + player.getName()))
                 .forEach(player -> {
             this.matchdays.addAll(this.voteForMatchday.stream().map(Pair::getKey).collect(Collectors.toList()));
             this.sortedMatchdays = this.sortMatchdays(this.matchdays);
             this.sortedMatchdays.forEach(matchDay ->
                 this.voteForMatchday.stream()
                         .filter(pair -> pair.getKey().equals(matchDay))
                         .forEach(pair -> {
                             this.sortedVoteForMatchday.add(new Pair<>(pair.getKey(), pair.getValue()));
                             //player.addVote(pair.getValue());
                         })
             );
             player.takeSortedVoteForMatchday(this.sortedVoteForMatchday);
             this.resetValues();
        });
    }

    private File getInfoFromSite(Season season) {

        final File file =
                new File(new File(FILE_BASE_PATH + season.getSeasonName() + FILE_EXTENSION).getAbsolutePath());
        try {
            file.createNewFile();
            final PrintWriter pw = new PrintWriter(file, StandardCharsets.UTF_8);
            final URL url = new URL(VOTE_BASE_URL + season.getSeasonName() + VOTE_PAGE_EXTENSION);
            final Scanner s = new Scanner(url.openStream());
            boolean info = false;
            while (s.hasNext()) {
                final String initLine = s.nextLine();
                if (initLine.contains("<tbody")) {
                    info = true;
                }
                while(info) {
                    final String line = s.nextLine();
                    if (line.contains("</tbody>")) {
                        info = false;
                    } else {
                        pw.println(line);
                    }
                }
            }
            pw.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
        return file;
    }

    private Set<Player> getPlayersFromFile(File file, Season season) {
        Set<Player> players = new HashSet<>();
        try {
            BufferedReader br = new BufferedReader(new FileReader(file));
            while(true){
                String initLine = br.readLine();
                if(initLine == null){
                    break;
                }
                else{
                    if(initLine.toLowerCase().contains("giornata") && initLine.contains("<tr")) {
                        String day = initLine.substring(initLine.indexOf("GIORNATA") + 9,
                                initLine.indexOf(">") - 1);

                        String playerName = this.getTdContent(br.readLine());
                        String team = this.getTdContent(br.readLine());
                        br.readLine(); //commented td line
                        String role = this.getTdContent(br.readLine());
                        final String fv = this.getTdContent(br.readLine());
                        final String v = this.getTdContent(br.readLine());

                        if(!role.isEmpty()){//empty role is for coaches
                            Player p = new Player(playerName, team, role);
                            int dayInt = Integer.parseInt(day) + season.getSeasonIndex()* SEASON_LENGTH;
                            double vDouble = v.equals(NO_VOTE) ? -1 : Double.parseDouble(v.replace(',','.'));
                            double fvDouble = fv.equals(NO_VOTE) ? -1 : Double.parseDouble(fv.replace(',','.'));
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

    private List<Player> getPlayerList(String season) {

        List<Player> result = new ArrayList<>();
        try {
            String filePath = "src/main/resources/lista_giocatori"+season+".xlsx";
            FileInputStream file = new FileInputStream(new File(filePath).getAbsolutePath());
            XSSFWorkbook workbook = new XSSFWorkbook (file);
            XSSFSheet sheet = workbook.getSheet("Tutti");

            Iterator<Row> rowIterator = sheet.iterator();

            rowIterator.next();
            rowIterator.next();

            while(rowIterator.hasNext()){
                Row row = rowIterator.next();
                if(row.getCell(0).getCellType().equals(CellType.NUMERIC)) {
                    result.add(new Player(row.getCell(1).getStringCellValue(), row.getCell(2).getStringCellValue(),
                            row.getCell(3).getStringCellValue(), (int) row.getCell(5).getNumericCellValue()));
                }
                else{
                    workbook.close();
                }
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
        return result;
    }

    /**
     * Return the content of html element td
     * @param line string containing the html element
     * @return
     */
    private String getTdContent(String line){
        return line.substring(line.indexOf("<td>") + 4, line.indexOf("</td>"));
    }

    private void resetValues() {
        this.matchdays.clear();
        this.sortedMatchdays.clear();
        this.voteForMatchday.clear();
        this.sortedVoteForMatchday.clear();
    }

    private List<Integer> sortMatchdays(List<Integer> days){
        days.sort(Comparator.comparingInt(a -> a));
        return days;
    }
}