package main;

import java.util.EnumSet;
import java.util.List;

enum Season {
    SEASON_1("2016-2017", 0),
    SEASON_2("2017-2018", 1),
    SEASON_3("2018-2019", 2);

    private final String seasonName;
    private final int seasonIndex;
    public static final int SEASON_LENGTH = 38;
    public static final int ALL_SEASONS_LENGTH = getAllSeasons().size() * SEASON_LENGTH;
    Season(String seasonName, int seasonIndex){
        this.seasonName = seasonName;
        this.seasonIndex = seasonIndex;
    }

    public static List<Season> getAllSeasons(){
        return List.of(Season.class.getEnumConstants());
    }

    public int getSeasonIndex() {
        return seasonIndex;
    }

    public String getSeasonName() {
        return seasonName;
    }


}
