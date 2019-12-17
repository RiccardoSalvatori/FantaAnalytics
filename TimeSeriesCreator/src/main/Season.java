package main;

enum Season {
    SEASON_1("2016-2017", 0),
    SEASON_2("2017-2018", 1),
    SEASON_3("2018-2019", 2);

    private final String seasonName;
    private final int seasonIndex;
    public static final int SEASON_LENGTH = 38;
    Season(String seasonName, int seasonIndex){
        this.seasonName = seasonName;
        this.seasonIndex = seasonIndex;
    }

    public int getSeasonIndex() {
        return seasonIndex;
    }

    public String getSeasonName() {
        return seasonName;
    }


}
