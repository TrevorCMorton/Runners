package rise;

import drl.AgentDependencyGraph;
import drl.MetaDecisionAgent;
import drl.agents.IAgent;
import drl.agents.MeleeButtonAgent;
import drl.agents.MeleeJoystickAgent;
import drl.servers.DummyTrainingServer;
import drl.servers.ITrainingServer;
import org.deeplearning4j.nn.graph.ComputationGraph;
import org.nd4j.linalg.api.ndarray.INDArray;
import org.nd4j.linalg.factory.Nd4j;
import org.nd4j.linalg.ops.transforms.Transforms;

import java.io.FileInputStream;
import java.io.InputStream;
import java.util.Properties;

public class RiseRunner {


    public static void main(String[] args) throws Exception{
        InputStream input = new FileInputStream("/home/trevor/Documents/dev/jpy/build/lib.linux-x86_64-3.6/jpyconfig.properties");
        Properties jpyProps = new Properties();
        // load a properties file
        jpyProps.load(input);

        Properties prop = System.getProperties();

        for(String property : jpyProps.stringPropertyNames()){
            prop.setProperty(property, (String)jpyProps.get(property));
        }

        RisePythonBridge bridge = new RisePythonBridge(args, MetaDecisionAgent.size);
        bridge.setup();

        float[] convFlatFrames = bridge.getState();
        INDArray convFrames = Nd4j.create(convFlatFrames, new int[]{MetaDecisionAgent.depth, MetaDecisionAgent.size, MetaDecisionAgent.size});

        AgentDependencyGraph dependencyGraph = new AgentDependencyGraph();
        IAgent joystickAgent = new MeleeJoystickAgent("M");
        IAgent cstickAgent = new MeleeJoystickAgent("C");
        IAgent abuttonAgent = new MeleeButtonAgent("A");
        dependencyGraph.addAgent(null, joystickAgent, "M");
        //dependencyGraph.addAgent(new String[]{"M"}, cstickAgent, "C");
        //dependencyGraph.addAgent(new String[]{"M"}, abuttonAgent, "A");
        ITrainingServer server = new DummyTrainingServer(dependencyGraph, "modelStick.mod");

        double prob = server.getProb();
        MetaDecisionAgent decisionAgent = new MetaDecisionAgent(dependencyGraph, prob);

        INDArray[] state = decisionAgent.getState(convFrames, new String[]{});

        decisionAgent.getOutputNames();

        INDArray[] masks = getMasks(1, new int[]{1, MetaDecisionAgent.depth, MetaDecisionAgent.size, MetaDecisionAgent.size}, .1);

        ComputationGraph graph = server.getUpdatedNetwork();

        INDArray[] trainedLabels = graph.output(state);

        INDArray[] errorSums = new INDArray[trainedLabels.length];

        for(int i = 0; i < errorSums.length; i++){
            errorSums[i] = Nd4j.zeros(convFrames.shape());
        }

        INDArray maskSum = Nd4j.zeros(convFrames.shape());

        for(int i = 0; i < masks.length; i++){
            maskSum = maskSum.add(masks[i]);

            INDArray maskedInput = convFrames.mul(masks[i]);
            INDArray[] maskedState = decisionAgent.getState(maskedInput, new String[]{});
            INDArray[] erroredLabels = graph.output(maskedState);

            for(int j = 0; j < errorSums.length; j++){
                INDArray maskLabelError = Transforms.abs(erroredLabels[j].sub(trainedLabels[j]));
                errorSums[j] = errorSums[j].add(maskLabelError);
            }
        }

        for(int j = 0; j < errorSums.length; j++){
            errorSums[j] = errorSums[j].div(maskSum);
            errorSums[j] = errorSums[j].div(errorSums[j].maxNumber());
        }

        String[] outputNames = decisionAgent.getOutputNames();
        for(int i = 0; i < 1/*outputNames.length*/; i++){
            bridge.outputImages(errorSums[i].toFloatVector(), outputNames[i]);
        }
    }

    private static INDArray[] getMasks(int num, int[] shape, double maskingChance){
        INDArray[] masks = new INDArray[num];
        INDArray middle = Nd4j.ones(shape).mul(maskingChance);

        for(int i = 0; i <  masks.length; i++){
            masks[i] = Transforms.greaterThanOrEqual(Nd4j.rand(shape), middle);
        }

        return masks;
    }
}
