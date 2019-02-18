package rise;

import org.jpy.PyLib;
import org.jpy.PyModule;
import org.jpy.PyObject;

import java.util.Properties;

public class RisePythonBridge {
    RiseSourcer source;

    public RisePythonBridge(String[] files, int size){
        PyLib.startPython();
        PyModule sys = PyModule.importModule("sys");
        PyObject pathObj = sys.getAttribute("path");

        String executionPath = System.getProperty("user.dir") + "/src/main/python";
        pathObj.call("append", executionPath);

        PyModule.importModule("p3");
        PyModule p4Module = PyModule.importModule("p3.rise_sourcer");
        PyObject plugInObj = p4Module.call("RiseSourcer", files, size);
        this.source = plugInObj.createProxy(RiseSourcer.class);
    }

    public void setup() {
        source.setup();
    }

    public float[] getState(){
        return source.get_state();
    }

    public void outputImages(float[] heats, String outputName){
        source.output_mapped_images(heats, outputName);
    }
}
