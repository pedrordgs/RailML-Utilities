import edu.mit.csail.sdg.ast.Command;
import edu.mit.csail.sdg.parser.CompModule;
import edu.mit.csail.sdg.parser.CompUtil;
import edu.mit.csail.sdg.translator.A4Options;
import edu.mit.csail.sdg.translator.A4Solution;
import edu.mit.csail.sdg.translator.TranslateAlloyToKodkod;

import java.io.File;
import java.util.stream.Collectors;

public class Generator {


    // input: {run name} {path to alloy file} {number of instances}
    public static void main(String[] args){
        String run = args[0];
        String alloyp = args[1];
        int n = Integer.parseInt(args[2]);
        CompModule model = CompUtil.parseEverything_fromFile(null, null, alloyp);
        Command cmd = model.getAllCommands().stream().filter(x -> x.toString().split(" ")[1].equals(run)).collect(Collectors.toList()).get(0);
        System.out.println();
        System.out.println("Command: " + cmd);
        System.out.println();
        File f = new File("/tmp/generated_models");
        f.mkdir();
        A4Solution solution= TranslateAlloyToKodkod.execute_command(null, model.getAllReachableSigs(), cmd, new A4Options());
        int counter = 0;
        while(counter++ < n && solution.satisfiable()){
            solution.writeXML("/tmp/generated_models/instance" + counter + ".xml");
            solution = solution.next();
        }
        System.out.println("Generated " + n + " instances");
    }
}