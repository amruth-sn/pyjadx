public class Caller {
    public static String callGreeter(String name) {
        Greeter g = new Greeter("Hi");
        return g.greet(name);
    }
}
