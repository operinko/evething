EVEthing.character = {
    anon_checked: null,
    
    onload: function() {
        EVEthing.misc.setup_tab_hash();

        $("#public-checkbox").change(EVEthing.character.public_checkbox_change);
        EVEthing.character.public_checkbox_change();

        EVEthing.character.anon_checked = $('#anon-key').prop('checked');
        $("#anon-key").change(EVEthing.character.anon_toggle);
        EVEthing.character.anon_toggle();
    },

    public_checkbox_change: function() {
        if (this.checked) {
            $('.disable-toggle').removeAttr("disabled");
        }
        else {
            $('.disable-toggle').attr("disabled", "disabled");
        }
    },

    anon_toggle: function() {
        var checked = $('#anon-key').prop('checked');
        if (checked != EVEthing.character.anon_checked) {
            $('#anon-key-link').remove();
            EVEthing.character.anon_checked = checked;
        }

        if (checked == true) {
            $("#anon-key-text").removeAttr("disabled");
            /*if ($("#anon-key-text").val() == "") {
                $("#anon-key-text").val(randString(16));
            }*/
        }
        else {
            $("#anon-key-text").attr("disabled", "");
            $("#anon-key-text").val("");
        }
    }
}
