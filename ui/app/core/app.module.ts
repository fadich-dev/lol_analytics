import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { AppComponent } from '../components/app/app.component';
import { MainFormComponent } from '../components/main_form/main_form.component';

@NgModule({
    imports: [BrowserModule],
    declarations: [AppComponent, MainFormComponent],
    bootstrap: [AppComponent],
})

export class AppModule {
}
