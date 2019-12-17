package main;

public class Pair<X,Y> {

    private final X x;
    private final Y y;

    /**
     * Constructor.
     * @param x
     *     item 1
     * @param y
     *     item 2
     */
    public Pair(final X x, final Y y) {
        this.x = x;
        this.y = y;
    }

    public X getKey() {
        return x;
    }

    public Y getValue() {
        return y;
    }

    @Override
    public String toString() {
        return "(" +this.x.toString() + "," + this.y.toString() + ")";
    }
}
