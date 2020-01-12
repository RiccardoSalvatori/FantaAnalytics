package main;

import java.util.*;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

public class Player {

    public static final double DEFAULT_VOTE = Double.NaN;

    private String name, team, role;
    private Map<Integer, Double> voteSeries;
    private Map<Integer, Double> fantaVoteSeries;

    public Player(String position, String fullName, String team, int initialQuotation){
        this.formatName(fullName);
        this.team = team;
        this.role = position;
        this.voteSeries = new HashMap<>();
        this.fantaVoteSeries = new HashMap<>();
    }

    public Player(String fullName, String team, String role){
        this.formatName(fullName);
        this.team = team;
        this.role = role;
        this.voteSeries = new HashMap<>();
        this.fantaVoteSeries = new HashMap<>();
    }

    public Player(Player p){
        this.name = p.name;
        this.team = p.team;
        this.role = p.role;
        this.voteSeries = new HashMap<>();
        this.fantaVoteSeries = new HashMap<>();
        this.voteSeries.putAll(p.getVoteSeries());
        this.fantaVoteSeries.putAll(p.getFantaVoteSeries());
    }

    private void formatName(String name){
        int[] upperCaseChars = name.chars().filter(Character::isUpperCase).toArray();
        this.name = new String(upperCaseChars, 0 , upperCaseChars.length) ;

    }

    public void addVote(int day, double vote){
        this.voteSeries.put(day,vote);
    }

    public void addFantaVote(int day, double fantaVote){
        this.fantaVoteSeries.put(day,fantaVote);
    }

    public String getName(){
        return this.name;
    }


    public String getTeam() {
        return this.team;
    }

    public String getRole() {
        return this.role;
    }

    public Map<Integer,Double> getVoteSeries() {
        return this.voteSeries;
    }

    public Map<Integer, Double> getFantaVoteSeries() {
        return this.fantaVoteSeries;
    }

    public void fillMissingVotesValues() {
        IntStream.range(1, Season.ALL_SEASONS_LENGTH+1).forEach(index -> {
            if(!this.voteSeries.containsKey(index)){
                this.addVote(index, DEFAULT_VOTE);
            }
        });
    }

    public void fillMissingFantaVotesValues() {
        IntStream.range(1, Season.ALL_SEASONS_LENGTH+1).forEach(index -> {
            if(!this.fantaVoteSeries.containsKey(index)){
                this.addFantaVote(index, DEFAULT_VOTE);
            }
        });
    }

    public String toString(){
        SortedSet<Integer> keys = new TreeSet<>(this.voteSeries.keySet()); //sort keys
        return this.name + ": " + this.role + "," + this.team + "," +
                keys.stream().map(k -> new Pair<>(k, voteSeries.get(k))).collect(Collectors.toList());
    }

    @Override
    public boolean equals(Object obj) {
        Player p = (Player) obj;
        return p.name.equals(this.name);
    }

    @Override
    public int hashCode() {
        // hash code only on name so that if two players have the same name they are equals in
        // collections iterations
        return Objects.hash(getName());
    }
}
