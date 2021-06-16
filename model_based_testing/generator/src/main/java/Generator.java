import edu.mit.csail.sdg.ast.Command;
import edu.mit.csail.sdg.parser.CompModule;
import edu.mit.csail.sdg.parser.CompUtil;
import edu.mit.csail.sdg.translator.A4Options;
import edu.mit.csail.sdg.translator.A4Solution;
import edu.mit.csail.sdg.translator.TranslateAlloyToKodkod;

public class Generator {

    public static void main(String[] args){
        CompModule model = CompUtil.parseEverything_fromFile(null, null, "/home/pbr/railML/alloy_related/another.als");
        Command cmd=model.getAllCommands().get(0);
        System.out.println(cmd.toString());
        A4Solution solution= TranslateAlloyToKodkod.execute_command(null, model.getAllReachableSigs(), cmd, new A4Options());
        int counter = 0;
        while(counter++ < 50 && solution.satisfiable()){
            solution.writeXML("/home/pbr/railML/model_based_testing/generated_models/instance" + counter + ".xml");
            solution = solution.next();
        }
    }
}