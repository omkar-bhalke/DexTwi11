package demo.notes;

import android.app.Activity;
import android.os.Bundle;
import android.view.View;
import android.widget.EditText;

public final class NotesActivity extends Activity {
    @Override protected void onCreate(Bundle state) {
        super.onCreate(state);
        setContentView(R.layout.notes);
    }

    public void saveDraft(View view) {
        EditText draft = findViewById(R.id.draft);
        getSharedPreferences("notes", MODE_PRIVATE).edit().putString("draft", draft.getText().toString()).apply();
    }
}
