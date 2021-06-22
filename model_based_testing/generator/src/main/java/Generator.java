import edu.mit.csail.sdg.alloy4.A4Reporter;
import edu.mit.csail.sdg.ast.Command;
import edu.mit.csail.sdg.parser.CompModule;
import edu.mit.csail.sdg.parser.CompUtil;
import edu.mit.csail.sdg.translator.A4Options;
import edu.mit.csail.sdg.translator.A4Solution;
import edu.mit.csail.sdg.translator.TranslateAlloyToKodkod;

import java.io.File;
import java.util.stream.Collectors;

public class Generator {
    private CompModule model;
    private A4Options options;
    private A4Reporter rep;

    public Generator(String alloyp){
        rep = new A4Reporter();
        options = new A4Options();
        options.solver = A4Options.SatSolver.MiniSatProverJNI;
        model = CompUtil.parseEverything_fromFile(rep, null, alloyp);
    }


    public void generateEveryNegRules(){
        File f = new File("generated_models");
        f.mkdir();
        for (int i=0;i<15;i++){
            if (i==8) continue;
            String run = "negRule" + i;
            Command cmd = model.getAllCommands().stream().filter(x -> x.toString().split(" ")[1].equals(run)).collect(Collectors.toList()).get(0);
            A4Solution solution= TranslateAlloyToKodkod.execute_command(rep, model.getAllReachableSigs(), cmd, options);
            if (solution.satisfiable()){
                solution.writeXML("generated_models/"+run+".xml");
            }
        }

        System.out.println("Generated an instance for every neg rule");
    }

    public void generateRun(String run, int n){
        Command cmd = model.getAllCommands().stream().filter(x -> x.toString().split(" ")[1].equals(run)).collect(Collectors.toList()).get(0);
        System.out.println();
        System.out.println("Command: " + cmd);
        System.out.println();
        File f = new File("/tmp/generated_models");
        f.mkdir();
        A4Solution solution= TranslateAlloyToKodkod.execute_command(rep, model.getAllReachableSigs(), cmd, options);
        int counter = 0;
        while(counter++ < n && solution.satisfiable()){
            solution.writeXML("/tmp/generated_models/instance" + counter + ".xml");
            solution = solution.next();
        }
        System.out.println("Generated " + n + " instances");
    }

    // input: {path to alloy file} {run name} {number of instances}    -    generates n instance from run
    // input: {path to alloy file}                                     -    generates an instance for each neg rule
    public static void main(String[] args) {
        String alloyp = args[0];
        Generator g = new Generator(alloyp);
        if (args.length == 1) {
            g.generateEveryNegRules();
        }
        if (args.length == 3) {
            String run = args[1];
            int n = Integer.parseInt(args[2]);
            g.generateRun(run, n);
        }
    }
}
