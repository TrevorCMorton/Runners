package rise;

public interface RiseSourcer {
    void setup();
    float[] get_state();
    float[] output_mapped_images(float[] heatValues, String outputName);
}
