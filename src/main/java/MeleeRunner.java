import drl.agents.IAgent;
import drl.agents.MeleeJoystickAgent;
import drl.AgentDependencyGraph;
import drl.MetaDecisionAgent;
import drl.servers.LocalTrainingServer;
import drl.servers.NetworkTrainingServer;
import org.deeplearning4j.nn.graph.ComputationGraph;
import org.nd4j.linalg.api.ndarray.INDArray;
import org.nd4j.linalg.factory.Nd4j;
import drl.servers.DummyTrainingServer;
import drl.servers.ITrainingServer;

import java.io.FileInputStream;
import java.io.InputStream;
import java.util.Properties;

public class MeleeRunner {
    public static final int loopTime = 100;

    public static void main(String[] args) throws Exception{
        InputStream input = new FileInputStream(args[2]);
        Properties jpyProps = new Properties();
        // load a properties file
        jpyProps.load(input);

        Properties prop = System.getProperties();

        for(String property : jpyProps.stringPropertyNames()){
            prop.setProperty(property, (String)jpyProps.get(property));
        }

        boolean sendData = Boolean.parseBoolean(args[1]);

        System.out.println("Launching Emulator");
        Runtime rt = Runtime.getRuntime();
        Process pr = rt.exec("/usr/games/dolphin-emu -e Melee.iso -u .dolphin-emu");

        System.out.println("Launching Training Server");
        int port = Integer.parseInt(args[4]);
        NetworkTrainingServer server;

        try {
            //server = new NetworkTrainingServer("hinton.csse.rose-hulman.edu");
            //ITrainingServer server = new NetworkTrainingServer("localhost");
            //server = new NetworkTrainingServer("ssbmvm1.csse.rose-hulman.edu");
            //server - new LocalTrainingServer(false, 10000, 128, );
            server = new NetworkTrainingServer("192.168.2.78", port);
        }
        catch (Exception e){
            System.out.println("Could not connect to server");
            pr.destroy();
            return;
        }

        Thread t = new Thread(server);
        t.start();

        AgentDependencyGraph dependencyGraph = server.getDependencyGraph();
        MetaDecisionAgent decisionAgent = new MetaDecisionAgent(dependencyGraph, Double.parseDouble(args[0]), 0);
        decisionAgent.setMetaGraph(server.getUpdatedNetwork());

        PythonBridge bridge = new PythonBridge(Boolean.parseBoolean(args[3]), MetaDecisionAgent.size);
        bridge.start();

        float[][] inputBuffer = new float[4][];

        for(int i = 0; i < inputBuffer.length; i++){
            inputBuffer[i] = new float[MetaDecisionAgent.size * MetaDecisionAgent.size];
        }

        INDArray[] prevActionMask = decisionAgent.getOutputMask(new String[0]);

        int[] shape = {1, 4, MetaDecisionAgent.size, MetaDecisionAgent.size};
        INDArray emptyFrame = Nd4j.zeros(shape);
        INDArray[] prevState = new INDArray[]{ emptyFrame, Nd4j.concat(1, prevActionMask) };

        long count = 0;
        long execTime = 0;

        while(true){
            long start = System.currentTimeMillis();

            if (bridge.isPostGame()){
                break;
            }

            INDArray frame = getFrame(bridge, inputBuffer);

            String[] results = decisionAgent.eval(frame);

            INDArray[] state = decisionAgent.getState(frame, results);

            bridge.execute(results);

            float curScore = bridge.getReward();

            INDArray[] mask = decisionAgent.getOutputMask(results);

            long end = System.currentTimeMillis();
            execTime += (end - start);
            if(end - start < MeleeRunner.loopTime) {
                if(curScore != 0) {
                    System.out.println(curScore);
                }

                if(sendData) {
                    server.addData(prevState, state, prevActionMask, curScore);
                }

                Thread.sleep(MeleeRunner.loopTime - (end - start));
            }
            else{
                System.out.println((end - start)  + " ms ");
            }

            prevState = state;
            prevActionMask = mask;

            count++;
        }

        System.out.println("Average execution time was " + (execTime / count));

        pr.destroy();
        //bridge.destroy();
        server.stop();
    }

    public static INDArray getFrame(PythonBridge bridge, float[][] inputBuffer){
        float[] inputFrame = bridge.getFlatFrame();
        for(int i = 0; i < inputBuffer.length; i++){
            float[] tempFrame = inputBuffer[i];
            inputBuffer[i] = inputFrame;
            inputFrame = tempFrame;
        }

        float[] flatFrame = new float[MetaDecisionAgent.size * MetaDecisionAgent.size * 4];
        int pos = 0;
        for(int i = 0; i < inputBuffer.length; i++){
            for(int j = 0; j < inputBuffer[i].length; j++){
                flatFrame[pos] = inputBuffer[i][j];
                pos++;
            }
        }

        int[] shape = {1, 4, MetaDecisionAgent.size, MetaDecisionAgent.size};
        INDArray frame = Nd4j.create(flatFrame, shape, 'c');

        return frame;
    }
}
