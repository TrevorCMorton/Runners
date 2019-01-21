package melee;

import drl.agents.IAgent;
import drl.agents.MeleeButtonAgent;
import drl.agents.MeleeJoystickAgent;
import drl.AgentDependencyGraph;
import drl.MetaDecisionAgent;
import drl.servers.NetworkTrainingServer;
import org.nd4j.linalg.api.ndarray.INDArray;
import org.nd4j.linalg.factory.Nd4j;
import drl.servers.DummyTrainingServer;
import drl.servers.ITrainingServer;

import java.io.FileInputStream;
import java.io.InputStream;
import java.util.Properties;

public class MeleeRunner {
    public static final int loopTime = 100;

    private static boolean saveHits = false;

    public static void main(String[] args) throws Exception{
        InputStream input = new FileInputStream(args[1]);
        Properties jpyProps = new Properties();
        // load a properties file
        jpyProps.load(input);

        Properties prop = System.getProperties();

        for(String property : jpyProps.stringPropertyNames()){
            prop.setProperty(property, (String)jpyProps.get(property));
        }

        boolean sendData = Boolean.parseBoolean(args[0]);

        System.out.println("Launching Emulator");
        Runtime rt = Runtime.getRuntime();
        Process pr = rt.exec("/usr/games/dolphin-emu -e Melee.iso -u .dolphin-emu");

        System.out.println("Launching Training Server");
        ITrainingServer server;

        try {
            server = new NetworkTrainingServer("hinton.csse.rose-hulman.edu");
            //server = new NetworkTrainingServer("localhost");
            //server = new NetworkTrainingServer("ssbmvm1.csse.rose-hulman.edu");
            //server - new LocalTrainingServer(false, 10000, 128, );
            //server = new NetworkTrainingServer("192.168.2.191");
            AgentDependencyGraph dependencyGraph = new AgentDependencyGraph();
            IAgent joystickAgent = new MeleeJoystickAgent("M");
            IAgent bbuttonAgent = new MeleeButtonAgent("B");
            IAgent cstickAgent = new MeleeJoystickAgent("C");
            IAgent abuttonAgent = new MeleeButtonAgent("A");
            dependencyGraph.addAgent(null, bbuttonAgent, "B");
            dependencyGraph.addAgent(new String[]{"B"}, joystickAgent, "M");
            //dependencyGraph.addAgent(new String[]{"M"}, cstickAgent, "C");
            //dependencyGraph.addAgent(new String[]{"M"}, abuttonAgent, "A");
            //server = new DummyTrainingServer(dependencyGraph, "/home/trevor/Runners/modelStickB.mod");
        }
        catch (Exception e){
            System.out.println("Could not connect to server" + e);
            pr.destroy();
            return;
        }

        Thread t = new Thread(server);
        t.start();

        AgentDependencyGraph dependencyGraph = server.getDependencyGraph();
        double prob = server.getProb();
        MetaDecisionAgent decisionAgent = new MetaDecisionAgent(dependencyGraph, prob);
        decisionAgent.setMetaGraph(server.getUpdatedNetwork());

        PythonBridge bridge = new PythonBridge(Boolean.parseBoolean(args[2]), MetaDecisionAgent.size, MetaDecisionAgent.depth, saveHits);
        bridge.start();

        INDArray[] prevActionMask = decisionAgent.getOutputMask(new String[0]);

        int[] shape = {1, MetaDecisionAgent.depth, MetaDecisionAgent.size, MetaDecisionAgent.size};
        INDArray emptyFrame = Nd4j.zeros(shape);
        INDArray[] prevState = new INDArray[]{ emptyFrame, Nd4j.concat(1, prevActionMask) };

        INDArray[] prevLabels = prevActionMask;

        double score = 0;

        long count = 0;
        long execTime = 0;
        long pythonTime = 0;
        long evalTime = 0;
        long stateTime = 0;
        long executeTime = 0;
        long rewardTime = 0;
        long masktime = 0;
        boolean upload = true;

        //server.pause();
        //t.suspend();

        while(true){
            long start = System.currentTimeMillis();

            if (bridge.isPostGame()){
                if(sendData && upload) {
                    INDArray[] curLabels = new INDArray[prevLabels.length];

                    for(int i = 0; i < curLabels.length; i++){
                        curLabels[i] = prevLabels[i].mul(-1).add(-1);
                    }

                    server.addData(prevState, prevState, prevActionMask, -1, prevLabels, curLabels);
                }
                break;
            }

            INDArray frame = getFrame(bridge);

            long pyTime = System.currentTimeMillis();
            pythonTime += (pyTime - start);

            String[] results = decisionAgent.eval(frame);

            long evTime = System.currentTimeMillis();
            evalTime += evTime - pyTime;

            INDArray[] state = decisionAgent.getState(frame, results);

            long stTime = System.currentTimeMillis();
            stateTime += stTime - evTime;

            float curScore = bridge.getReward();
            score += curScore;
            INDArray[] curLabels = decisionAgent.getCachedLabels();

            if(sendData && upload) {
                server.addData(prevState, state, prevActionMask, curScore, prevLabels, curLabels);
            }

            long rewTime = System.currentTimeMillis();
            rewardTime += rewTime - stTime;

            bridge.execute(results);

            long exTime = System.currentTimeMillis();
            executeTime += exTime - rewTime;

            INDArray[] mask = decisionAgent.getOutputMask(results);

            long end = System.currentTimeMillis();
            masktime += (end - exTime);
            if(end - start < MeleeRunner.loopTime) {
                upload = true;

                if(curScore != 0) {
                    System.out.println(curScore);
                }

                Thread.sleep(MeleeRunner.loopTime - (end - start));
            }
            else{
                upload = false;
                System.out.println((end - start)  + " ms ");
            }

            prevState = state;
            prevActionMask = mask;
            prevLabels = curLabels;

            count++;
        }

        System.out.println("Average execution time was " + (execTime / count));
        System.out.println("Average python time was " + (pythonTime / count));
        System.out.println("Average eval time was " + (evalTime / count));
        System.out.println("Average state time was " + (stateTime / count));
        System.out.println("Average execute time was " + (executeTime / count));
        System.out.println("Average reward time was " + (rewardTime / count));
        System.out.println("Average mask time was " + (masktime / count));
        decisionAgent.printEvalSummary();

        server.addScore(score);

        pr.destroy();
        //bridge.destroy();
        //t.resume();
        //server.resume();
        server.stop();
    }

    public static INDArray getFrame(PythonBridge bridge){
        float[] inputFrame = bridge.getFlatFrame();
        int[] shape = {1, MetaDecisionAgent.depth, MetaDecisionAgent.size, MetaDecisionAgent.size};
        INDArray frame = Nd4j.create(inputFrame, shape, 'c');

        return frame;
    }
}
